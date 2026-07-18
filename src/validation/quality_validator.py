"""Data completeness, duplicate, type, and business-rule validation."""

from typing import Any, Dict, List

import pandas as pd


class QualityValidator:
    """Profiles data payloads for value ranges, completeness, and formats."""

    @staticmethod
    def _numeric_column(
        df: pd.DataFrame, column: str, issues: List[str], allow_embedded_number: bool = False
    ) -> pd.Series:
        """Coerce numeric values and support documented vendor formats such as '4.6 out of 5 stars'."""
        numeric = pd.to_numeric(df[column], errors="coerce")
        if allow_embedded_number:
            extracted = pd.to_numeric(
                df[column].astype("string").str.extract(r"([-+]?\d*\.?\d+)", expand=False), errors="coerce"
            )
            numeric = numeric.fillna(extracted)
        malformed = df[column].notna() & numeric.isna()
        if malformed.any():
            issues.append(f"{int(malformed.sum())} records have a non-numeric value in '{column}'.")
        return numeric

    def profile_and_check(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        total_rows = len(df)
        null_counts = df.isnull().sum().to_dict()
        duplicate_count = int(df.duplicated().sum())
        issues: List[str] = []
        critical_null_columns = {
            "users": ["user_id"],
            "products": ["product_id", "product_name"],
            "reviews": ["review_id", "user_id", "product_id"],
            "sessions": ["session_id", "user_id"],
            "clickstream": ["event_id", "session_id", "user_id", "product_id"],
        }

        if duplicate_count:
            issues.append(f"{duplicate_count} duplicate records found.")
        for column in critical_null_columns.get(dataset_name, []):
            null_count = int(df[column].isna().sum()) if column in df.columns else total_rows
            if null_count:
                issues.append(f"{null_count} records have a missing required value in '{column}'.")

        if dataset_name == "reviews" and "rating" in df.columns:
            ratings = self._numeric_column(df, "rating", issues)
            invalid = df[(ratings < 1) | (ratings > 5)]
            if not invalid.empty:
                issues.append(f"{len(invalid)} records fell outside rating scale 1-5.")

        if dataset_name == "products":
            if "price" in df.columns:
                prices = self._numeric_column(df, "price", issues)
                negative = df[prices < 0]
                if not negative.empty:
                    issues.append(f"{len(negative)} products contained negative prices.")
            if "avg_rating" in df.columns:
                average_ratings = self._numeric_column(df, "avg_rating", issues, allow_embedded_number=True)
                invalid = df[(average_ratings < 0) | (average_ratings > 5)]
                if not invalid.empty:
                    issues.append(f"{len(invalid)} products have avg_rating outside 0-5.")

        if dataset_name == "users" and "age" in df.columns:
            ages = self._numeric_column(df, "age", issues)
            invalid = df[(ages < 0) | (ages > 120)]
            if not invalid.empty:
                issues.append(f"{len(invalid)} users have age outside 0-120.")

        if dataset_name == "sessions" and "session_duration_sec" in df.columns:
            durations = self._numeric_column(df, "session_duration_sec", issues)
            invalid = df[durations < 0]
            if not invalid.empty:
                issues.append(f"{len(invalid)} sessions have a negative duration.")

        if dataset_name == "users" and "email" in df.columns:
            invalid_emails = df[~df["email"].astype(str).str.contains("@", na=False)]
            if not invalid_emails.empty:
                issues.append(f"{len(invalid_emails)} users have invalid email structures.")

        return {
            "total_records": total_rows,
            "duplicate_records": duplicate_count,
            "null_value_distributions": null_counts,
            "validation_issues_found": issues,
            "is_valid": not issues,
        }
