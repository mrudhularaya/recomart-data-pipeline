# src/features/feature_runner.py
import sys
import sqlite3
from pathlib import Path
import pandas as pd

# Path configurations to access global tools
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger

def run_feature_pipeline():
    logger.info("Initializing Feature Engineering & Database Transformation engine...", extra={"pipeline_step": "FEATURE_START"})
    
    project_root = Path(src_dir).parent
    processed_dir = project_root / "data" / "processed"
    warehouse_dir = project_root / "data" / "warehouse"
    warehouse_dir.mkdir(exist_ok=True)
    
    db_path = warehouse_dir / "recomart_warehouse.db"

    # Verify input source files are accessible
    users_file = processed_dir / "users" / "users.csv"
    products_file = processed_dir / "products" / "products.csv"
    reviews_file = processed_dir / "reviews" / "reviews.csv"
    sessions_file = processed_dir / "sessions" / "sessions.csv"

    if not (users_file.exists() and products_file.exists() and reviews_file.exists()):
        logger.critical("Aborting transformation: Base processed source CSV matrices are missing.")
        return

    # Read clean prepared data layers
    users_df = pd.read_csv(users_file)
    products_df = pd.read_csv(products_file)
    reviews_df = pd.read_csv(reviews_file)
    sessions_df = pd.read_csv(sessions_file)

    logger.info("Calculating aggregate interaction and rating metrics...", extra={"pipeline_step": "FEATURE_ENG"})

    # -------------------------------------------------------------
    # ALGORITHMIC FEATURE GENERATION
    # -------------------------------------------------------------
    
    # Feature 1: User Activity Frequency (Session counts per user)
    user_activity = sessions_df.groupby("user_id").size().reset_index(name="user_activity_frequency")
    
    # Feature 2: Average Rating Given per User
    user_avg_rating = reviews_df.groupby("user_id")["rating"].mean().reset_index(name="user_avg_rating")
    
    # Merge engineered metrics directly onto our User foundation profile
    transformed_users = users_df.merge(user_activity, on="user_id", how="left")
    transformed_users = transformed_users.merge(user_avg_rating, on="user_id", how="left")
    
    # Gracefully fill unengaged or unmapped rows with neutral metrics
    transformed_users["user_activity_frequency"] = transformed_users["user_activity_frequency"].fillna(0).astype(int)
    transformed_users["user_avg_rating"] = transformed_users["user_avg_rating"].fillna(0.0)

    # Feature 3: Average Rating Earned per Item
    item_avg_rating = reviews_df.groupby("product_id")["rating"].mean().reset_index(name="item_avg_rating")
    
    # Feature 4: Total Reviews Count per Item (Item Popularity Index)
    item_review_count = reviews_df.groupby("product_id").size().reset_index(name="item_interaction_count")
    
    # Merge engineered metrics directly onto our Product baseline profile
    transformed_products = products_df.merge(item_avg_rating, on="product_id", how="left")
    transformed_products = transformed_products.merge(item_review_count, on="product_id", how="left")
    
    transformed_products["item_avg_rating"] = transformed_products["item_avg_rating"].fillna(0.0)
    transformed_products["item_interaction_count"] = transformed_products["item_interaction_count"].fillna(0).astype(int)

    # For Feast
    transformed_users["created_timestamp"] = "2026-07-12 00:00:00"
    transformed_products["created_timestamp"] = "2026-07-12 00:00:00"


    # -------------------------------------------------------------
    # SQLITE DATABASE STRUCTURE COMMITS
    # -------------------------------------------------------------
    logger.info(f"Opening relational database execution connection at: data/warehouse/recomart_warehouse.db", extra={"pipeline_step": "DB_LOAD"})
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Explicit Relational Tables matching Task 6 DDL Deliverables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_users (
            user_id TEXT PRIMARY KEY,
            age INTEGER,
            gender TEXT,
            city TEXT,
            membership TEXT,
            signup_year INTEGER,
            user_activity_frequency INTEGER,
            user_avg_rating REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            brand TEXT,
            price REAL,
            item_avg_rating REAL,
            item_interaction_count INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_interactions (
            review_id TEXT PRIMARY KEY,
            user_id TEXT,
            product_id TEXT,
            rating REAL,
            sentiment_encoded INTEGER,
            FOREIGN KEY (user_id) REFERENCES dim_users(user_id),
            FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
        )
    """)
    conn.commit()

    # Slice tables down to select columns matching our SQL schema constraints
    users_sql_payload = transformed_users[[
        "user_id", "age", "gender", "city", "membership", 
        "signup_year", "user_activity_frequency", "user_avg_rating"
    ]]
    
    products_sql_payload = transformed_products[[
        "product_id", "product_name", "category", "brand", 
        "price", "item_avg_rating", "item_interaction_count"
    ]]
    
    interactions_sql_payload = reviews_df[[
        "review_id", "user_id", "product_id", "rating", "sentiment_encoded"
    ]]

    # Stream out pandas structures straight into SQLite tables using overwrite appends
    users_sql_payload.to_sql("dim_users", conn, if_exists="replace", index=False)
    products_sql_payload.to_sql("dim_products", conn, if_exists="replace", index=False)
    interactions_sql_payload.to_sql("fact_interactions", conn, if_exists="replace", index=False)

    # Read totals out of SQL database rows to provide a formal metric audit checkpoint confirmation
    cursor.execute("SELECT COUNT(*) FROM dim_users")
    db_users_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM dim_products")
    db_products_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM fact_interactions")
    db_interactions_count = cursor.fetchone()[0]

    conn.close()
    
    # Print out a clear summary card for project verification
    print("\n" + "="*50)
    print("💾 TASK 6 FEATURE WAREHOUSE COMMITS COMPLETE")
    print("="*50)
    print(f"🔹 Rows written to dim_users       : {db_users_count:,}")
    print(f"🔹 Rows written to dim_products    : {db_products_count:,}")
    print(f"🔹 Rows written to fact_interactions: {db_interactions_count:,}")
    print(f"🔹 Output database path            : data/warehouse/recomart_warehouse.db")
    print("="*50 + "\n")

    logger.info("Feature engineering transformation and relational database loading cycles completed.", extra={"pipeline_step": "FEATURE_END"})

if __name__ == "__main__":
    run_feature_pipeline()
