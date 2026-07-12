# src/validation/quality_validator.py
import pandas as pd
from typing import Dict, Any

class QualityValidator:
    """Profiles data payloads for value ranges, completeness, and formats."""

    def profile_and_check(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        total_rows = len(df)
        null_counts = df.isnull().sum().to_dict()
        duplicate_count = int(df.duplicated().sum())
        issues = []

        # Automated format & range checks 
        if dataset_name == "reviews" and "rating" in df.columns:
            # Range test: scale 1–5
            out_of_range = df[(df["rating"] < 1) | (df["rating"] > 5)]
            if not out_of_range.empty:
                issues.append(f"{len(out_of_range)} records fell outside rating scale 1–5.")

        if dataset_name == "products" and "price" in df.columns:
            # Format/Value check
            negative_prices = df[df["price"] < 0]
            if not negative_prices.empty:
                issues.append(f"{len(negative_prices)} products contained negative prices.")

        if dataset_name == "users" and "email" in df.columns:
            # Format pattern verification
            invalid_emails = df[~df["email"].astype(str).str.contains("@", na=False)]
            if not invalid_emails.empty:
                issues.append(f"{len(invalid_emails)} users have invalid email structures.")

        return {
            "total_records": total_rows,
            "duplicate_records": duplicate_count,
            "null_value_distributions": null_counts,
            "validation_issues_found": issues,
            "is_valid": len(issues) == 0
        }
