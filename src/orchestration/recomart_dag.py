# src/orchestration/recomart_dag.py
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

from prefect import flow, task

# Resolve absolute search paths to target your project modules safely
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger
from ingestion.run_ingestion import main as run_ingestion_func
from validation.validation_runner import run_validation_pipeline as run_validation_func
from preparation.preparation_runner import run_preparation_pipeline as run_preparation_func
from features.feature_runner import run_feature_pipeline as run_features_func
from models.train_eval import RecomartModelSuite

# --- DEFINE ISOLATED PREFECT TASKS ---
# Each decorator creates an trackable execution node matching an Airflow Operator

@task(name="Data Ingestion & Staging", retries=1, retry_delay_seconds=120)
def ingest_task_node():
    logger.info("[Prefect Task] Running Data Ingestion sub-routine...")
    run_ingestion_func()

@task(name="Data Profiling & Validation")
def validate_task_node():
    logger.info("[Prefect Task] Running Data Validation checks & compiling PDF...")
    run_validation_func()

@task(name="Data Preparation & Imputation")
def prepare_task_node():
    logger.info("[Prefect Task] Running Data Cleansing & Normalization scaling...")
    run_preparation_func()

@task(name="Feature Engineering & SQL Warehouse Load")
def feature_task_node():
    logger.info("[Prefect Task] Calculating recommendation metrics & writing to SQLite...")
    run_features_func()

@task(name="Recommendation Model Training & MLflow Tracking")
def train_task_node():
    logger.info("[Prefect Task] Running popularity baselines and TF-IDF similarity matrix...")
    suite = RecomartModelSuite()
    suite.run_training_lifecycle(top_k=5)


# --- THE MASTER CONTROL FLOW GRAPH ---
# The @flow decorator glues individual tasks together into a managed sequence

@flow(name="Recomart End-to-End Recommendation Pipeline")
def recomart_orchestration_flow():
    logger.info("Prefect orchestration flow initializing sequential steps...", extra={"pipeline_step": "DAG_START"})
    
    # Enforce sequential pipeline execution order (Ingest -> Validate -> Prepare -> Features -> Train)
    ingest_task_node()
    validate_task_node()
    prepare_task_node()
    feature_task_node()
    train_task_node()
    
    logger.info("Prefect orchestration flow execution completed smoothly.", extra={"pipeline_step": "DAG_SUCCESS"})


if __name__ == "__main__":
    # Execute the master automation pipeline natively on Windows
    recomart_orchestration_flow()
