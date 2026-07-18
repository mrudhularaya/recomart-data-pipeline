from typing import List, Dict

class FeatureView:
    """Defines and documents feature names, source tables, types, and logic."""
    def __init__(self, name: str, source_table: str, join_key: str, features: Dict[str, str], description: str):
        self.name = name
        self.source_table = source_table
        self.join_key = join_key
        self.features = features  # Maps feature name to data type
        self.description = description

# Document User Engineered Features
user_features_view = FeatureView(
    name="user_features",
    source_table="dim_users",
    join_key="user_id",
    description="Algorithmic user profiles capturing activity frequencies and average scoring behaviors.",
    features={
        "age": "INTEGER (Min-Max Normalized)",
        "gender": "TEXT",
        "city": "TEXT",
        "membership": "TEXT",
        "user_activity_frequency": "INTEGER (Aggregated Session Count via Task 6)",
        "user_avg_rating": "REAL (Calculated Baseline Mean via Task 6)"
    }
)

# Document Product Engineered Features
product_features_view = FeatureView(
    name="product_features",
    source_table="dim_products",
    join_key="product_id",
    description="Algorithmic product profiles tracking price distributions and interaction popularity indices.",
    features={
        "product_name": "TEXT",
        "category": "TEXT",
        "brand": "TEXT",
        "price": "REAL (Log Normalized)",
        "item_avg_rating": "REAL (Calculated Performance Mean via Task 6)",
        "item_interaction_count": "INTEGER (Aggregated Popularity Volume via Task 6)"
    }
)
