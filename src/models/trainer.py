"""Train recommendation models using a per-user holdout evaluation protocol."""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Tuple

import mlflow
import pandas as pd

src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger
from models.content_based import ContentBasedTFIDFModel
from models.evaluator import RecommenderEvaluator
from models.popularity import PopularityBaselineModel


class RecommendationPipelineTrainer:
    def __init__(self):
        self.project_root = Path(src_dir).parent
        self.db_path = self.project_root / "data" / "warehouse" / "recomart_warehouse.db"
        self.artifact_path = self.project_root / "artifacts" / "recommendations.json"
        self.mlflow_db = self.project_root / "mlflow.db"

    def _load_data_warehouse(self):
        with sqlite3.connect(self.db_path) as conn:
            interactions = pd.read_sql_query("SELECT * FROM fact_interactions", conn)
            products = pd.read_sql_query("SELECT * FROM dim_products", conn)
            users = pd.read_sql_query("SELECT * FROM dim_users", conn)
        return users, products, interactions

    @staticmethod
    def _split_interactions(interactions: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Hold out the latest interaction for each user with at least two interactions."""
        ordered = interactions.copy()
        ordered["review_date"] = pd.to_datetime(ordered["review_date"], errors="coerce")
        ordered = ordered.sort_values(["user_id", "review_date", "review_id"], na_position="first")
        eligible = ordered.groupby("user_id")["review_id"].transform("size") >= 2
        test_indices = ordered[eligible].groupby("user_id").tail(1).index
        return ordered.drop(index=test_indices), ordered.loc[test_indices]

    def _log_evaluation(self, model_name, recommendations, test, top_k):
        precision, recall, ndcg = RecommenderEvaluator.evaluate_at_k(test, recommendations, k=top_k)
        mlflow.log_param("model_type", model_name)
        mlflow.log_param("top_k_evaluation", top_k)
        mlflow.log_metric(f"Precision_at_{top_k}", precision)
        mlflow.log_metric(f"Recall_at_{top_k}", recall)
        mlflow.log_metric(f"NDCG_at_{top_k}", ndcg)
        return {"precision_at_k": precision, "recall_at_k": recall, "ndcg_at_k": ndcg}

    def train_and_track_all(self, top_k: int = 5):
        if not self.db_path.exists():
            raise FileNotFoundError(f"SQLite Database missing at {self.db_path}")
        users, products, interactions = self._load_data_warehouse()
        train, test = self._split_interactions(interactions)
        if test.empty:
            raise ValueError("At least one user needs two interactions for holdout evaluation.")
        # Do not inherit a machine-wide MLflow SQLite configuration, which may be read-only.
        mlflow.set_tracking_uri(f"sqlite:///{self.mlflow_db.resolve().as_posix()}")
        mlflow.set_experiment("Recomart_Recommendation_System")

        with mlflow.start_run(run_name="Popularity_Baseline") as run:
            pop_recs = PopularityBaselineModel().recommend(users, products, top_k=top_k)
            pop_metrics = self._log_evaluation("Popularity_Baseline", pop_recs, test, top_k)
            pop_run_id = run.info.run_id

        with mlflow.start_run(run_name="Content_Based_TFIDF") as run:
            content_recs = ContentBasedTFIDFModel().recommend(users, products, train, top_k=top_k)
            content_metrics = self._log_evaluation("Content_Based_TFIDF", content_recs, test, top_k)
            payload = {
                "model": "content_based_tfidf",
                "top_k": top_k,
                "generated_from_training_interactions": len(train),
                "recommendations": content_recs,
                "metrics": content_metrics,
            }
            self.artifact_path.parent.mkdir(exist_ok=True)
            self.artifact_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            mlflow.log_artifact(str(self.artifact_path))
            content_run_id = run.info.run_id

        result = {
            "train_interactions": len(train), "test_interactions": len(test),
            "popularity": {"run_id": pop_run_id, **pop_metrics},
            "content_based": {"run_id": content_run_id, **content_metrics},
            "inference_artifact": str(self.artifact_path),
        }
        logger.info(f"Model training complete: {result}", extra={"pipeline_step": "TRAIN_COMPLETE"})
        evaluation_summary = {
            "evaluation_strategy": "Per-user holdout",
            "top_k": top_k,
            "train_interactions": len(train),
            "test_interactions": len(test),
            "n_test_users": test["user_id"].nunique(),
            "models": [
                {
                    "model": "Popularity",
                    "precision_at_5": pop_metrics["precision_at_k"],
                    "recall_at_5": pop_metrics["recall_at_k"],
                    "ndcg_at_5": pop_metrics["ndcg_at_k"],
                },
                {
                    "model": "ContentBased-TFIDF",
                    "precision_at_5": content_metrics["precision_at_k"],
                    "recall_at_5": content_metrics["recall_at_k"],
                    "ndcg_at_5": content_metrics["ndcg_at_k"],
                }
            ]
        }
        artifact_dir = self.project_root / "artifacts"
        artifact_dir.mkdir(exist_ok=True)

        # JSON
        json_path = artifact_dir / "model_evaluation.json"
        json_path.write_text(
            json.dumps(evaluation_summary, indent=2),
            encoding="utf-8"
        )

        # CSV
        csv_path = artifact_dir / "model_evaluation.csv"
        pd.DataFrame(evaluation_summary["models"]).to_csv(csv_path, index=False)
        
        # Markdown
        md_path = artifact_dir / "model_evaluation.md"

        lines = [
            "# Recommendation Model Evaluation",
            "",
            "## Evaluation Summary",
            "",
            "| Property | Value |",
            "|----------|-------|",
            f"| Evaluation Strategy | {evaluation_summary['evaluation_strategy']} |",
            f"| Top-K | {evaluation_summary['top_k']} |",
            f"| Training Interactions | {evaluation_summary['train_interactions']} |",
            f"| Test Interactions | {evaluation_summary['test_interactions']} |",
            f"| Test Users | {evaluation_summary['n_test_users']} |",
            "",
            "## Evaluation Metrics",
            "",
            "| Model | Precision@5 | Recall@5 | NDCG@5 |",
            "|------|-------------:|----------:|--------:|",
        ]

        # Iterate over the list of models, not the dictionary itself
        for row in evaluation_summary["models"]:
            lines.append(
                f"| {row['model']} | "
                f"{row['precision_at_5']:.6f} | "
                f"{row['recall_at_5']:.6f} | "
                f"{row['ndcg_at_5']:.6f} |"
            )

        lines.extend([
            "",
            "### Evaluation Strategy",
            "",
            "The recommendation models were evaluated using a per-user holdout evaluation strategy.",
            "For each eligible user, the latest interaction was reserved for testing.",
            "",
            "The following ranking metrics were computed:",
            "",
            "- Precision@5",
            "- Recall@5",
            "- NDCG@5",
        ])

        md_path.write_text("\n".join(lines), encoding="utf-8")

        logger.info(
            f"Model evaluation reports generated at: {artifact_dir}",
            extra={"pipeline_step": "TRAIN_REPORT_GENERATED"}
        )

        return result


if __name__ == "__main__":
    print(json.dumps(RecommendationPipelineTrainer().train_and_track_all(), indent=2))
