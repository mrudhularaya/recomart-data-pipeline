import sys
import json
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

# Dynamic path resolution to keep imports clean
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.logger import logger
from validation.schema_validator import SchemaValidator
from validation.quality_validator import QualityValidator
from validation.report_generator import generate_validation_pdf

def run_validation_pipeline():
    logger.info("Initializing Data Validation engine...", extra={"pipeline_step": "VALIDATE_START"})
    
    project_root = Path(src_dir).parent
    raw_dir = project_root / "data" / "raw"
    validated_dir = project_root / "data" / "validated"
    reports_dir = project_root / "reports"
    
    reports_dir.mkdir(exist_ok=True)
    
    schema_engine = SchemaValidator()
    quality_engine = QualityValidator()
    
    quality_report = {
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "datasets_profiled": {}
    }

    if not raw_dir.exists():
        logger.critical(f"Aborting validation: Raw directory missing at {raw_dir}")
        return

    # Loop dynamically through each dataset domain folder inside the data lake
    for dataset_folder in raw_dir.iterdir():
        if not dataset_folder.is_dir():
            continue
            
        dataset_name = dataset_folder.name
        
        # Grab the latest timestamp/date partition directory automatically
        date_folders = sorted([d for d in dataset_folder.iterdir() if d.is_dir()])
        if not date_folders:
            continue
            
        latest_partition = date_folders[-1]
        target_csv = latest_partition / f"{dataset_name}.csv"
        
        if not target_csv.exists():
            continue

        logger.info(f"Profiling raw landing zone data for: [{dataset_name}]", extra={"pipeline_step": "VALIDATE_LOOP"})
        
        # Read from raw data lake partition
        df = pd.read_csv(target_csv)
        
        # Run tests
        schema_passed, schema_errors = schema_engine.validate(df, dataset_name)
        quality_metrics = quality_engine.profile_and_check(df, dataset_name)
        
        quality_report["datasets_profiled"][dataset_name] = {
            "schema_check_passed": schema_passed,
            "schema_errors": schema_errors,
            **quality_metrics
        }

        # Route directly to data/validated/ without performing cleaning operations
        if schema_passed and quality_metrics["is_valid"]:
            output_path_dir = validated_dir / dataset_name
            output_path_dir.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(output_path_dir / f"{dataset_name}.csv", index=False)
            logger.info(f"Successfully staged validated copy to data/validated/{dataset_name}/")
        else:
            logger.error(
                f"Dataset [{dataset_name}] failed validation: "
                f"schema_errors={schema_errors}; quality_issues={quality_metrics['validation_issues_found']}"
            )

    # Output Quality Report Deliverable
    report_file_path = reports_dir / "validation_report.json"
    with open(report_file_path, "w", encoding="utf-8") as f:
        json.dump(quality_report, f, indent=2)

    generate_validation_pdf(quality_report, reports_dir / "validation_report.pdf")
        
    logger.info("Data Quality Reports written to reports/validation_report.json and .pdf", extra={"pipeline_step": "VALIDATE_END"})
    return quality_report

if __name__ == "__main__":
    run_validation_pipeline()
