# src/preparation/preparation_runner.py
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Path configurations to tap utilities
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger

def run_preparation_pipeline():
    logger.info("Initializing Data Preparation engine...", extra={"pipeline_step": "PREPARE_START"})
    
    project_root = Path(src_dir).parent
    validated_dir = project_root / "data" / "validated"
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(exist_ok=True)

    if not validated_dir.exists():
        logger.critical("Aborting preparation: Source data/validated/ directory is missing.")
        return

    # -------------------------------------------------------------
    # PIPELINE 1: USERS PREPARATION
    # -------------------------------------------------------------
    users_path = validated_dir / "users" / "users.csv"
    if users_path.exists():
        logger.info("Preparing 'users' dataset...", extra={"pipeline_step": "PREPARE_LOOP"})
        users_df = pd.read_csv(users_path)
        
        # Deduplication
        users_df = users_df.drop_duplicates(subset=["user_id"], keep="first")
        
        # Fill Missing (Null) values 
        users_df["age"] = users_df["age"].fillna(users_df["age"].median())
        users_df["gender"] = users_df["gender"].fillna("Unknown")
        
        # Categorical Encoding (Label Encoding via category codes)
        users_df["gender_encoded"] = users_df["gender"].astype("category").cat.codes
        users_df["membership_encoded"] = users_df["membership"].astype("category").cat.codes
        users_df["segment_encoded"] = users_df["customer_segment"].astype("category").cat.codes
        
        # Date Parsing
        users_df["signup_date"] = pd.to_datetime(users_df["signup_date"], errors="coerce")
        users_df["signup_year"] = users_df["signup_date"].dt.year.fillna(0).astype(int)
        users_df["signup_month"] = users_df["signup_date"].dt.month.fillna(0).astype(int)
        
        # Numerical Normalization (Min-Max scale Age between 0 and 1)
        age_min, age_max = users_df["age"].min(), users_df["age"].max()
        if age_max > age_min:
            users_df["age_normalized"] = (users_df["age"] - age_min) / (age_max - age_min)
        else:
            users_df["age_normalized"] = 0.0

        # Save to output zone
        out_dir = processed_dir / "users"
        out_dir.mkdir(exist_ok=True)
        users_df.to_csv(out_dir / "users.csv", index=False)
        logger.info(f"Staged cleaned and prepared users table ({len(users_df)} rows).")

    # -------------------------------------------------------------
    # PIPELINE 2: PRODUCTS PREPARATION
    # -------------------------------------------------------------
    products_path = validated_dir / "products" / "products.csv"
    if products_path.exists():
        logger.info("Preparing 'products' dataset...", extra={"pipeline_step": "PREPARE_LOOP"})
        products_df = pd.read_csv(products_path)
        
        # Deduplication
        products_df = products_df.drop_duplicates(subset=["product_id"], keep="first")
        
        # Fill Missing values
        products_df["price"] = products_df["price"].fillna(products_df["price"].median())
        products_df["avg_rating"] = products_df["avg_rating"].fillna(0.0)
        
        # Categorical Encoding
        products_df["category_encoded"] = products_df["category"].astype("category").cat.codes
        products_df["brand_encoded"] = products_df["brand"].astype("category").cat.codes
        
        # Numerical Normalization (Log transformation on Price to stabilize skewness)
        # Adding 1 to prevent log(0) issues
        products_df["price_log_normalized"] = np.log1p(products_df["price"].clip(lower=0))
        
        out_dir = processed_dir / "products"
        out_dir.mkdir(exist_ok=True)
        products_df.to_csv(out_dir / "products.csv", index=False)
        logger.info(f"Staged cleaned and prepared products table ({len(products_df)} rows).")

    # -------------------------------------------------------------
    # PIPELINE 3: REVIEWS PREPARATION
    # -------------------------------------------------------------
    reviews_path = validated_dir / "reviews" / "reviews.csv"
    if reviews_path.exists():
        logger.info("Preparing 'reviews' dataset...", extra={"pipeline_step": "PREPARE_LOOP"})
        reviews_df = pd.read_csv(reviews_path)
        
        # Deduplication
        reviews_df = reviews_df.drop_duplicates(subset=["review_id"], keep="first")
        
        # Drop rows missing critical interaction links (User-Item connection check)
        reviews_df = reviews_df.dropna(subset=["user_id", "product_id"])
        
        # Handle missing ratings by falling back to the item default mid-scale
        reviews_df["rating"] = reviews_df["rating"].fillna(3.0)
        
        # Encode sentiment classifications
        reviews_df["sentiment_encoded"] = reviews_df["sentiment"].astype("category").cat.codes
        
        # Handle chronological transformations
        reviews_df["review_date"] = pd.to_datetime(reviews_df["review_date"], errors="coerce")
        
        out_dir = processed_dir / "reviews"
        out_dir.mkdir(exist_ok=True)
        reviews_df.to_csv(out_dir / "reviews.csv", index=False)
        logger.info(f"Staged cleaned and prepared reviews table ({len(reviews_df)} rows).")

    # -------------------------------------------------------------
    # PIPELINE 4: SESSIONS & CLICKSTREAM PREPARATION
    # -------------------------------------------------------------
    sessions_path = validated_dir / "sessions" / "sessions.csv"
    if sessions_path.exists():
        logger.info("Preparing 'sessions' dataset...", extra={"pipeline_step": "PREPARE_LOOP"})
        sessions_df = pd.read_csv(sessions_path)
        
        sessions_df = sessions_df.drop_duplicates(subset=["session_id"], keep="first")
        sessions_df["session_duration_sec"] = sessions_df["session_duration_sec"].fillna(0)
        
        # Min-Max Normalization on session durations
        dur_min, dur_max = sessions_df["session_duration_sec"].min(), sessions_df["session_duration_sec"].max()
        if dur_max > dur_min:
            sessions_df["duration_normalized"] = (sessions_df["session_duration_sec"] - dur_min) / (dur_max - dur_min)
        else:
            sessions_df["duration_normalized"] = 0.0
            
        out_dir = processed_dir / "sessions"
        out_dir.mkdir(exist_ok=True)
        sessions_df.to_csv(out_dir / "sessions.csv", index=False)
        logger.info(f"Staged cleaned and prepared sessions table ({len(sessions_df)} rows).")

    logger.info("Data Preparation processing routines executed completely.", extra={"pipeline_step": "PREPARE_END"})

if __name__ == "__main__":
    run_preparation_pipeline()
