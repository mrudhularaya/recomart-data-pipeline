import pandas as pd
import numpy as np
from typing import List, Dict, Tuple

class RecommenderEvaluator:
    """Calculates evaluation matrix profiles across generated recommendations."""
    
    @staticmethod
    def evaluate_at_k(test_interactions: pd.DataFrame, recommendations_map: Dict[str, List[str]], k: int = 5) -> Tuple[float, float, float]:
        precisions = []
        recalls = []
        ndcgs = []
        
        for user_id in test_interactions['user_id'].unique():
            true_items = set(test_interactions[test_interactions['user_id'] == user_id]['product_id'].tolist())
            predicted_items = recommendations_map.get(str(user_id), [])[:k]
            
            if not true_items or not predicted_items:
                continue
                
            intersection = set(predicted_items).intersection(true_items)
            
            precision = len(intersection) / len(predicted_items)
            recall = len(intersection) / len(true_items)
            
            precisions.append(precision)
            recalls.append(recall)
            dcg = sum(1 / np.log2(rank + 2) for rank, item in enumerate(predicted_items) if item in true_items)
            ideal_dcg = sum(1 / np.log2(rank + 2) for rank in range(min(len(true_items), k)))
            ndcgs.append(dcg / ideal_dcg if ideal_dcg else 0.0)
            
        mean_p = float(np.mean(precisions)) if precisions else 0.0
        mean_r = float(np.mean(recalls)) if recalls else 0.0
        mean_ndcg = float(np.mean(ndcgs)) if ndcgs else 0.0
        return mean_p, mean_r, mean_ndcg
