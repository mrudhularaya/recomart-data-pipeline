"""Generate a portable PDF data-quality report from validation results."""

from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_validation_pdf(report: Dict[str, Any], output_path: Path) -> None:
    """Write a concise, submission-ready validation summary PDF."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    story = [Paragraph("RecoMart Data Quality Report", styles["Title"])]
    story.append(Paragraph(f"Generated: {report['execution_timestamp']}", styles["Normal"]))
    story.append(Spacer(1, 0.35 * cm))

    rows = [["Dataset", "Rows", "Duplicates", "Schema", "Quality", "Issues"]]
    for name, metrics in report["datasets_profiled"].items():
        issue_text = "; ".join(metrics["validation_issues_found"]) or "None"
        rows.append([
            name,
            str(metrics["total_records"]),
            str(metrics["duplicate_records"]),
            "Pass" if metrics["schema_check_passed"] else "Fail",
            "Pass" if metrics["is_valid"] else "Fail",
            issue_text,
        ])

    table = Table(rows, colWidths=[2.0 * cm, 1.4 * cm, 1.7 * cm, 1.5 * cm, 1.5 * cm, 9.0 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EAF2F8")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "Datasets are promoted to the validated zone only when both schema and quality checks pass. "
        "Null distributions are retained in validation_report.json for column-level review.",
        styles["BodyText"],
    ))
    SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=1 * cm, leftMargin=1 * cm).build(story)
