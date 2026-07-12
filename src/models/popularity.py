import pandas as pd
from typing import List, Dict

class PopularityBaselineModel:
    """Ranks and recommends products based on interactions count and average ratings."""
    
    def recommend(self, users_df: pd.DataFrame, products_df: pd.DataFrame, top_k: int = 5) -> Dict[str, List[str]]:
        # Identify top N highly-reviewed products with best ratings
        top_products = products_df.sort_values(by=["item_interaction_count", "item_avg_rating"], ascending=False)
        baseline_recommendations = top_products["product_id"].head(top_k).tolist()
        
        # Broadcast the static top list across all user profiles
        return {str(uid): baseline_recommendations for uid in users_df["user_id"]}
