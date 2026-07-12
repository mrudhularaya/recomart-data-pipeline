# src/models/train_eval.py
import sys
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import mlflow

# Path configurations to tap global structures
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger

class RecomartModelSuite:
    """Trains, evaluates, and tracks recommendation algorithm variants using MLflow."""
    
    def __init__(self):
        self.project_root = Path(src_dir).parent
        self.db_path = self.project_root / "data" / "warehouse" / "recomart_warehouse.db"
        
    def _load_data_from_warehouse(self):
        """Extracts data elements out of the SQLite warehouse layers."""
        conn = sqlite3.connect(self.db_path)
        
        # Load interactions and dimension definitions
        interactions_df = pd.read_sql_query("SELECT * FROM fact_interactions", conn)
        products_df = pd.read_sql_query("SELECT * FROM dim_products", conn)
        users_df = pd.read_sql_query("SELECT * FROM dim_users", conn)
        
        conn.close()
        return users_df, products_df, interactions_df

    def _calculate_metrics_at_k(self, test_interactions, recommendations_map, k=5):
        """Computes Precision@K and Recall@K across evaluation sets."""
        precisions = []
        recalls = []
        
        for user_id in test_interactions['user_id'].unique():
            # True positive items liked/interacted by user
            true_items = set(test_interactions[test_interactions['user_id'] == user_id]['product_id'].tolist())
            
            # Top N items predicted by the model view
            predicted_items = recommendations_map.get(str(user_id), [])[:k]
            
            if not true_items or not predicted_items:
                continue
                
            intersection = set(predicted_items).intersection(true_items)
            
            precision = len(intersection) / len(predicted_items)
            recall = len(intersection) / len(true_items)
            
            precisions.append(precision)
            recalls.append(recall)
            
        return float(np.mean(precisions)), float(np.mean(recalls))

    def run_training_lifecycle(self, top_k=5):
        logger.info("Initializing Task 9 Recommendation Model Training pipeline...", extra={"pipeline_step": "TRAIN_START"})
        
        if not self.db_path.exists():
            logger.critical(f"Aborting training: SQLite Database missing at {self.db_path}")
            return
            
        users, products, interactions = self._load_data_from_warehouse()
        
        # Set up an isolated MLflow Experiment Workspace
        mlflow.set_experiment("Recomart_Recommendation_System")
        
        # -------------------------------------------------------------
        # RUN 1: POPULARITY BASELINE ENGINE
        # -------------------------------------------------------------
        with mlflow.start_run(run_name="Popularity_Baseline"):
            logger.info("Training Popularity Baseline model variant...", extra={"pipeline_step": "TRAIN_POPULARITY"})
            
            # Log Model Parameters to MLflow
            mlflow.log_param("model_type", "Popularity_Baseline")
            mlflow.log_param("top_k_evaluation", top_k)
            
            # Identify top N highly-reviewed products with best ratings
            top_products = products.sort_values(by=["item_interaction_count", "item_avg_rating"], ascending=False)
            baseline_recommendations = top_products["product_id"].head(top_k).tolist()
            
            # Broadcast the static top list across evaluation mapping tables
            popularity_recs_map = {str(uid): baseline_recommendations for uid in users["user_id"]}
            
            # Evaluate baseline precision/recall matrices
            p_at_k, r_at_k = self._calculate_metrics_at_k(interactions, popularity_recs_map, k=top_k)
            
            # Log Metrics into MLflow
            mlflow.log_metric(f"Precision_at_{top_k}", p_at_k)
            mlflow.log_metric(f"Recall_at_{top_k}", r_at_k)
            
            logger.info(f"Popularity Baseline Metrics logged -> Precision: {p_at_k:.4f}, Recall: {r_at_k:.4f}")

        # -------------------------------------------------------------
        # RUN 2: CONTENT-BASED TF-IDF ENGINE
        # -------------------------------------------------------------
        with mlflow.start_run(run_name="Content_Based_TFIDF"):
            logger.info("Training Content-Based TF-IDF Similarity engine...", extra={"pipeline_step": "TRAIN_CONTENT"})
            
            mlflow.log_param("model_type", "Content_Based_TFIDF")
            mlflow.log_param("vectorizer", "TfidfVectorizer")
            mlflow.log_param("top_k_evaluation", top_k)
            
            # Fill string spaces gracefully before building vocab tokens
            products["product_name"] = products["product_name"].fillna("")
            products["category"] = products["category"].fillna("")
            products["description"] = products["description"].fillna("")
            
            # Generate corporate text metadata tokens array
            metadata_corpus = products["product_name"] + " " + products["category"] + " " + products["description"]
            
            # Text vectorization conversions via TF-IDF
            tfidf = TfidfVectorizer(stop_words="english", max_features=1000)
            tfidf_matrix = tfidf.fit_transform(metadata_corpus)
            
            # Compute Cosine Similarity distance weights matrix
            cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
            
            # Map user historical purchase data to generate personalized similarity lists
            content_recs_map = {}
            product_id_to_idx = {pid: idx for idx, pid in enumerate(products["product_id"])}
            idx_to_product_id = {idx: pid for idx, pid in enumerate(products["product_id"])}
            
            for user_id in users["user_id"]:
                # Grab user's past raw purchases entries
                user_history = interactions[interactions["user_id"] == user_id]["product_id"].tolist()
                
                if not user_history:
                    # Fallback default back to popularity criteria if user metadata trace is blank
                    content_recs_map[str(user_id)] = baseline_recommendations
                    continue
                    
                # Collect weights vector matches across item maps
                sim_scores = np.zeros(len(products))
                for pid in user_history:
                    if pid in product_id_to_idx:
                        sim_scores += cosine_sim_matrix[product_id_to_idx[pid]]
                        
                # Sort indices based on similarity score matches
                top_indices = np.argsort(sim_scores)[::-1]
                
                # Exclude items the user has already bought to avoid self-recommendation
                recommended_pids = [idx_to_product_id[idx] for idx in top_indices if idx_to_product_id[idx] not in user_history]
                
                # Ensure the final recommended list is backfilled to match top_k length
                if len(recommended_pids) < top_k:
                    recommended_pids.extend([item for item in baseline_recommendations if item not in recommended_pids])
                    
                content_recs_map[str(user_id)] = recommended_pids[:top_k]
                
            # Evaluate Content-Based engine profiles
            p_at_k_cb, r_at_k_cb = self._calculate_metrics_at_k(interactions, content_recs_map, k=top_k)
            
            mlflow.log_metric(f"Precision_at_{top_k}", p_at_k_cb)
            mlflow.log_metric(f"Recall_at_{top_k}", r_at_k_cb)
            
            print("\n" + "="*50)
            print("🚀 TASK 9 MODEL TRAINING & METRICS LOGGING COMPLETE")
            print("="*50)
            print(f"🔹 MLflow Experiment Name  : Recomart_Recommendation_System")
            print(f"🔹 Popularity Baseline P@5  : {p_at_k:.4f}")
            print(f"🔹 Content-Based TF-IDF P@5 : {p_at_k_cb:.4f}")
            print(f"🔹 Evaluation Metrics Shape : Precision@5 & Recall@5 logs captured")
            print("="*50 + "\n")
            
            logger.info("Model training suite and MLflow tracking complete.", extra={"pipeline_step": "TRAIN_COMPLETE"})

if __name__ == "__main__":
    suite = RecomartModelSuite()
    # Run the standard training pipeline
    suite.run_training_lifecycle(top_k=5)
    
    # VERIFICATION TEST: Pull live data and verify User 123 recommendations
    try:
        users_df, products_df, interactions_df = suite._load_data_from_warehouse()
        
        # Guard clause: Pick a user ID that actually exists in your database row index
        available_user_ids = users_df["user_id"].unique()
        test_user = "123" if "123" in available_user_ids else str(available_user_ids[0])
        
        print("\n" + "🔍" + "="*48)
        print(f"LIVE INFRASTRUCTURE TEST: RECOMMENDATIONS FOR USER [{test_user}]")
        print("="*50)
        
        # Simulating our Content-Based Inference Matrix Loop inline for verification
        # Look up user past purchases
        user_history = interactions_df[interactions_df["user_id"] == test_user]["product_id"].tolist()
        
        # Run TF-IDF corpus assembly identically
        products_df["product_name"] = products_df["product_name"].fillna("")
        products_df["category"] = products_df["category"].fillna("")
        products_df["description"] = products_df["description"].fillna("")
        metadata_corpus = products_df["product_name"] + " " + products_df["category"] + " " + products_df["description"]
        
        tfidf = TfidfVectorizer(stop_words="english", max_features=1000)
        tfidf_matrix = tfidf.fit_transform(metadata_corpus)
        cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        product_id_to_idx = {pid: idx for idx, pid in enumerate(products_df["product_id"])}
        idx_to_product_id = {idx: pid for idx, pid in enumerate(products_df["product_id"])}
        
        # Gather text similarity scores
        sim_scores = np.zeros(len(products_df))
        for pid in user_history:
            if pid in product_id_to_idx:
                sim_scores += cosine_sim_matrix[product_id_to_idx[pid]]
                
        top_indices = np.argsort(sim_scores)[::-1]
        recommended_pids = [idx_to_product_id[idx] for idx in top_indices if idx_to_product_id[idx] not in user_history][:5]
        
        # Print recommendations to verify structural output
        print(f"🔹 Historical item purchases count: {len(user_history)}")
        print(f"🔹 Generated recommendations count : {len(recommended_pids)}")
        print("-" * 50)
        
        for idx, rec_pid in enumerate(recommended_pids, 1):
            prod_row = products_df[products_df["product_id"] == rec_pid].iloc[0]
            print(f"📍 Rec #{idx}: ID: {rec_pid} | {prod_row['product_name']} ({prod_row['category']})")
            
        print("="*50 + "\n")
        logger.info("Verification step complete: Core engine successfully outputs recommendations.")
        
    except Exception as eval_err:
        print(f"❌ Verification test failed to map items: {str(eval_err)}")

