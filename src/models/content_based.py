import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

class ContentBasedTFIDFModel:
    """Generates personalized text-matching product recommendations using TF-IDF."""
    
    def recommend(self, users_df: pd.DataFrame, products_df: pd.DataFrame, 
                  interactions_df: pd.DataFrame, top_k: int = 5) -> Dict[str, List[str]]:
        
        # 1. Fill missing string blanks safely across text columns
        products_df["product_name"] = products_df["product_name"].fillna("")
        products_df["category"] = products_df["category"].fillna("")
        products_df["description"] = products_df["description"].fillna("")
        
        # 2. Assemble enhanced metadata textual corpus
        metadata_corpus = products_df["product_name"] + " " + products_df["category"] + " " + products_df["description"]
        
        # 3. Compute TF-IDF matrix vectors and Cosine Distance weights
        tfidf = TfidfVectorizer(stop_words="english", max_features=1000)
        tfidf_matrix = tfidf.fit_transform(metadata_corpus)
        cosine_sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        product_id_to_idx = {pid: idx for idx, pid in enumerate(products_df["product_id"])}
        idx_to_product_id = {idx: pid for idx, pid in enumerate(products_df["product_id"])}
        
        # Generate baseline fallback list for cold-start entries
        top_products = products_df.sort_values(by=["item_interaction_count", "item_avg_rating"], ascending=False)
        fallback_recs = top_products["product_id"].head(top_k).tolist()
        
        content_recs_map = {}
        for user_id in users_df["user_id"]:
            user_history = interactions_df[interactions_df["user_id"] == user_id]["product_id"].tolist()
            
            if not user_history:
                content_recs_map[str(user_id)] = fallback_recs
                continue
                
            sim_scores = np.zeros(len(products_df))
            for pid in user_history:
                if pid in product_id_to_idx:
                    sim_scores += cosine_sim_matrix[product_id_to_idx[pid]]
                    
            top_indices = np.argsort(sim_scores)[::-1]
            recommended_pids = [idx_to_product_id[idx] for idx in top_indices if idx_to_product_id[idx] not in user_history]
            
            if len(recommended_pids) < top_k:
                recommended_pids.extend([item for item in fallback_recs if item not in recommended_pids])
                
            content_recs_map[str(user_id)] = recommended_pids[:top_k]
            
        return content_recs_map
