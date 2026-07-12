# src/validation/schema_validator.py
import pandas as pd
from typing import Dict, List, Tuple

class SchemaValidator:
    """Validates structural integrity and column presence of incoming datasets."""
    
    def __init__(self):
        self.expected_schemas: Dict[str, List[str]] = {
            "users": [
                "user_id", "age", "gender", "city", "membership", 
                "preferred_category", "signup_date", "customer_segment", "is_active"
            ],
            "sessions": [
                "session_id", "user_id", "session_start", "session_end", "device", 
                "browser", "traffic_source", "session_duration_sec", "pages_visited", 
                "bounce", "conversion"
            ],
            "reviews": [
                "review_id", "user_id", "product_id", "rating", 
                "review_text", "sentiment", "verified_purchase", "review_date"
            ],
            "products": [
                "product_id", "product_name", "category", "brand", "price", 
                "avg_rating", "rating_count", "availability", "bestseller_rank", "description"
            ],
            "clickstream": [
                "event_id", "session_id", "user_id", "product_id",
                "event_timestamp", "event_type", "page", "device",
                "browser", "traffic_source", "dwell_time_sec", "recommendation_flag"

                ]
        }

    def validate(self, df: pd.DataFrame, dataset_name: str) -> Tuple[bool, List[str]]:
        errors = []
        expected_cols = self.expected_schemas.get(dataset_name, [])
        
        if not expected_cols:
            return True, errors

        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Schema mismatch! Missing expected columns: {missing_cols}")
            
        return len(errors) == 0, errors
