# src/orchestration/recomart_dag.py
import sys
import time
import os
from pathlib import Path
from datetime import datetime, timezone

# Dynamic path resolution to keep imports clean
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Keep Prefect's temporary-server SQLite state inside the project, where it is writable
# and isolated from other local Prefect installations.
project_root = Path(src_dir).parent
prefect_home = project_root / ".prefect_runtime"
prefect_home.mkdir(parents=True, exist_ok=True)
os.environ["PREFECT_HOME"] = str(prefect_home.resolve())
os.environ["DO_NOT_TRACK"] = "1"

from models.trainer import RecommendationPipelineTrainer

from prefect import flow, task

# Resolve absolute search paths to target your project modules safely
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger
from ingestion.run_ingestion import main as run_ingestion_func
from validation.validation_runner import run_validation_pipeline as run_validation_func
from preparation.preparation_runner import run_preparation_pipeline as run_preparation_func
from feature_engineering.feature_runner import run_feature_pipeline as run_features_func
from feature_store.materialize import RecomartFeatureStore
from governance.lineage import IngestionLineageTracker
from preparation.eda import generate_eda_plots
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
    generate_eda_plots()

@task(name="Feature Engineering & SQL Warehouse Load")
def feature_task_node():
    logger.info("[Prefect Task] Calculating recommendation metrics & writing to SQLite...")
    run_features_func()

@task(name="Feature Store Materialization")
def feature_store_task_node():
    logger.info("[Prefect Task] Materializing versioned online features...")
    RecomartFeatureStore().materialize_store()

@task(name="Data Lineage Manifest")
def lineage_task_node():
    logger.info("[Prefect Task] Generating data lineage manifest...")
    IngestionLineageTracker().log_lineage_run()

@task(name="Recommendation Model Training & MLflow Tracking")
def train_task_node():
    logger.info("[Prefect Task] Running popularity baselines and TF-IDF similarity matrix...")
    # Instantiate the updated split trainer module class name
    trainer = RecommendationPipelineTrainer()
    trainer.train_and_track_all(top_k=5)


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
    feature_store_task_node()
    train_task_node()
    lineage_task_node()
    
    logger.info("Prefect orchestration flow execution completed smoothly.", extra={"pipeline_step": "DAG_SUCCESS"})


if __name__ == "__main__":
    # Execute the master automation pipeline natively on Windows
    recomart_orchestration_flow()
