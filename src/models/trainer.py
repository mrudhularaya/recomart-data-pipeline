import sys
import sqlite3
from pathlib import Path
import pandas as pd
import mlflow

src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger
from models.popularity import PopularityBaselineModel
from models.content_based import ContentBasedTFIDFModel
from models.evaluator import RecommenderEvaluator

class RecommendationPipelineTrainer:
    """Handles the model training coordination lifecycle and hooks up MLflow logs."""
    
    def __init__(self):
        self.project_root = Path(src_dir).parent
        self.db_path = self.project_root / "data" / "warehouse" / "recomart_warehouse.db"
        
    def _load_data_warehouse(self):
        conn = sqlite3.connect(self.db_path)
        interactions_df = pd.read_sql_query("SELECT * FROM fact_interactions", conn)
        products_df = pd.read_sql_query("SELECT * FROM dim_products", conn)
        users_df = pd.read_sql_query("SELECT * FROM dim_users", conn)
        conn.close()
        return users_df, products_df, interactions_df

    def train_and_track_all(self, top_k: int = 5):
        logger.info("Initializing Task 9 Decoupled Model Training pipeline...", extra={"pipeline_step": "TRAIN_START"})
        
        if not self.db_path.exists():
            logger.critical(f"Aborting training: SQLite Database missing at {self.db_path}")
            return
            
        users, products, interactions = self._load_data_warehouse()
        mlflow.set_experiment("Recomart_Recommendation_System")
        
        # --- MODEL 1: POPULARITY RUN ---
        with mlflow.start_run(run_name="Popularity_Baseline"):
            logger.info("Training Popularity Baseline model variant...", extra={"pipeline_step": "TRAIN_POPULARITY"})
            mlflow.log_param("model_type", "Popularity_Baseline")
            mlflow.log_param("top_k_evaluation", top_k)
            
            pop_model = PopularityBaselineModel()
            pop_recs = pop_model.recommend(users, products, top_k=top_k)
            
            p_at_k, r_at_k = RecommenderEvaluator.evaluate_at_k(interactions, pop_recs, k=top_k)
            mlflow.log_metric(f"Precision_at_{top_k}", p_at_k)
            mlflow.log_metric(f"Recall_at_{top_k}", r_at_k)
            logger.info(f"Popularity Baseline Metrics logged -> Precision: {p_at_k:.4f}, Recall: {r_at_k:.4f}")

        # --- MODEL 2: CONTENT-BASED RUN ---
        with mlflow.start_run(run_name="Content_Based_TFIDF"):
            logger.info("Training Content-Based TF-IDF Similarity engine...", extra={"pipeline_step": "TRAIN_CONTENT"})
            mlflow.log_param("model_type", "Content_Based_TFIDF")
            mlflow.log_param("top_k_evaluation", top_k)
            
            cb_model = ContentBasedTFIDFModel()
            cb_recs = cb_model.recommend(users, products, interactions, top_k=top_k)
            
            p_at_k_cb, r_at_k_cb = RecommenderEvaluator.evaluate_at_k(interactions, cb_recs, k=top_k)
            mlflow.log_metric(f"Precision_at_{top_k}", p_at_k_cb)
            mlflow.log_metric(f"Recall_at_{top_k}", r_at_k_cb)
            
            print("\n" + "="*50)
            print("🚀 TASK 9 MODEL DECOUPLED LIFECYCLE COMPLETE")
            print("="*50)
            print(f"🔹 MLflow Experiment Workspace : Recomart_Recommendation_System")
            print(f"🔹 Popularity Baseline P@5     : {p_at_k:.4f}")
            print(f"🔹 Content-Based TF-IDF P@5    : {p_at_k_cb:.4f}")
            print("="*50 + "\n")
            
        # --- LIVE VERIFICATION CODE TARGET FOR USER U00001 ---
        try:
            available_user_ids = users["user_id"].unique()
            test_user = "U00001" if "U00001" in available_user_ids else str(available_user_ids[0])
            user_recs = cb_recs.get(test_user, [])
            
            print("🔍" + "="*48)
            print(f"LIVE INFRASTRUCTURE TEST: RECOMMENDATIONS FOR USER [{test_user}]")
            print("="*50)
            print(f"🔹 Generated recommendations count: {len(user_recs)}")
            print("-" * 50)
            for idx, rec_pid in enumerate(user_recs, 1):
                prod_row = products[products["product_id"] == rec_pid].iloc[0]
                print(f"📍 Rec #{idx}: ID: {rec_pid} | {prod_row['product_name']} ({prod_row['category']})")
            print("="*50 + "\n")
        except Exception as eval_err:
            print(f"❌ Verification test failed to map items: {str(eval_err)}")

        logger.info("Model training suite and MLflow tracking complete.", extra={"pipeline_step": "TRAIN_COMPLETE"})

if __name__ == "__main__":
    trainer = RecommendationPipelineTrainer()
    trainer.train_and_track_all(top_k=5)
