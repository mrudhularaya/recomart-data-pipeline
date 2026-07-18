"""Create recommendation features and load them into a SQLite star schema."""

import sqlite3
import sys
from pathlib import Path

import pandas as pd

src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger


def _create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        PRAGMA foreign_keys = ON;
        -- Rebuild derived tables on every feature run so schema migrations are deterministic.
        DROP TABLE IF EXISTS online_feature_cache;
        DROP TABLE IF EXISTS fact_interactions;
        DROP TABLE IF EXISTS dim_users;
        DROP TABLE IF EXISTS dim_products;
        CREATE TABLE IF NOT EXISTS dim_users (
            user_id TEXT PRIMARY KEY,
            age REAL,
            gender TEXT,
            city TEXT,
            membership TEXT,
            signup_year INTEGER,
            user_activity_frequency INTEGER NOT NULL,
            user_avg_rating REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS dim_products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT,
            brand TEXT,
            price REAL,
            item_avg_rating REAL NOT NULL,
            item_interaction_count INTEGER NOT NULL,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS fact_interactions (
            review_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            rating REAL NOT NULL CHECK (rating BETWEEN 1 AND 5),
            sentiment_encoded INTEGER,
            review_date TEXT,
            FOREIGN KEY (user_id) REFERENCES dim_users(user_id),
            FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
        );
    """)


def run_feature_pipeline():
    logger.info("Initializing Feature Engineering & Database Transformation engine...", extra={"pipeline_step": "FEATURE_START"})
    project_root = Path(src_dir).parent
    processed_dir = project_root / "data" / "processed"
    warehouse_dir = project_root / "data" / "warehouse"
    warehouse_dir.mkdir(exist_ok=True)

    required = {name: processed_dir / name / f"{name}.csv" for name in ("users", "products", "reviews", "sessions")}
    missing = [str(path) for path in required.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Processed inputs missing: {', '.join(missing)}")

    users_df = pd.read_csv(required["users"])
    products_df = pd.read_csv(required["products"])
    reviews_df = pd.read_csv(required["reviews"])
    sessions_df = pd.read_csv(required["sessions"])

    user_activity = sessions_df.groupby("user_id").size().rename("user_activity_frequency")
    user_avg_rating = reviews_df.groupby("user_id")["rating"].mean().rename("user_avg_rating")
    transformed_users = users_df.join(user_activity, on="user_id").join(user_avg_rating, on="user_id")
    transformed_users["user_activity_frequency"] = transformed_users["user_activity_frequency"].fillna(0).astype(int)
    transformed_users["user_avg_rating"] = transformed_users["user_avg_rating"].fillna(0.0)

    item_avg_rating = reviews_df.groupby("product_id")["rating"].mean().rename("item_avg_rating")
    item_count = reviews_df.groupby("product_id").size().rename("item_interaction_count")
    transformed_products = products_df.join(item_avg_rating, on="product_id").join(item_count, on="product_id")
    transformed_products["item_avg_rating"] = transformed_products["item_avg_rating"].fillna(0.0)
    transformed_products["item_interaction_count"] = transformed_products["item_interaction_count"].fillna(0).astype(int)

    users_payload = transformed_users[["user_id", "age", "gender", "city", "membership", "signup_year", "user_activity_frequency", "user_avg_rating"]]
    products_payload = transformed_products[["product_id", "product_name", "category", "brand", "price", "item_avg_rating", "item_interaction_count", "description"]]
    interactions_payload = reviews_df[["review_id", "user_id", "product_id", "rating", "sentiment_encoded", "review_date"]]

    db_path = warehouse_dir / "recomart_warehouse.db"
    with sqlite3.connect(db_path) as conn:
        _create_schema(conn)
        # Append into the declared schema so keys and checks are preserved.
        users_payload.to_sql("dim_users", conn, if_exists="append", index=False)
        products_payload.to_sql("dim_products", conn, if_exists="append", index=False)
        interactions_payload.to_sql("fact_interactions", conn, if_exists="append", index=False)
        counts = {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ("dim_users", "dim_products", "fact_interactions")}

    logger.info(f"Warehouse loaded: {counts}", extra={"pipeline_step": "FEATURE_END"})
    return {"database": str(db_path), **counts}


if __name__ == "__main__":
    run_feature_pipeline()
