import os
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)

# Brand color palette
BRAND_BLUE = "#004B8D"
BRAND_ORANGE = "#F58025"
BRAND_GREEN = "#76A240"

# CONFIGURATION
REPORT_TITLE = "SOO Preclose Financial Report"
# Resolve paths relative to this file so it works regardless of the current
# working directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")  # Place your company logo here
RESULTS_CSV = os.path.join(BASE_DIR, "results.csv")  # Path to your results data
OUTPUT_PDF = os.path.join(BASE_DIR, "SOO_Preclose_Report.pdf")


# Helper to build table data from a DataFrame
def dataframe_to_table(df: pd.DataFrame) -> List[List[str]]:
    table = [df.columns.tolist()]
    for _, row in df.iterrows():
        table.append([str(x) for x in row.tolist()])
    return table


def main() -> None:
    # 1. Load Data
    df = pd.read_csv(RESULTS_CSV)

    # Calculate basic counts
    total_points = len(df)
    match_count = (df["Result"] == "Match").sum()
    mismatch_df = df[df["Result"] != "Match"]
    mismatch_count = len(mismatch_df)

    # Use only mismatches marked as "Does Not Match" for the report
    df = df[df["Result"] == "Does Not Match"]

    # Calculate total absolute variance per account for a bar chart
    TOP_N = 10
    abs_var_df = (
        df.groupby("CAReport Name")["Variance"]
        .apply(lambda x: x.abs().sum())
        .reset_index(name="Total Absolute Variance")
    )
    abs_var_df = abs_var_df.sort_values("Total Absolute Variance", ascending=False).head(TOP_N)

    # Aggregate metrics including totals for Excel and Database values
    key_metrics = (
        df.groupby("CAReport Name")[["Variance", "Excel Value", "DataBase Value"]]
        .sum()
        .reset_index()
    )
    key_metrics.columns = [
        "CAReport Name",
        "Total Variance",
        "Total Excel Value",
        "Total Database Value",
    ]
    key_metrics = key_metrics.merge(abs_var_df, on="CAReport Name")
    key_metrics = key_metrics.sort_values("Total Absolute Variance", ascending=False).head(TOP_N)

    plt.figure(figsize=(6, 4))
    plt.barh(
        key_metrics["CAReport Name"],
        key_metrics["Total Absolute Variance"],
        color=BRAND_BLUE,
    )
    plt.xlabel("Total Absolute Variance")
    plt.ylabel("CAReport Name")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    bar_chart_path = os.path.join(BASE_DIR, "top_abs_variance.png")
    plt.savefig(bar_chart_path, bbox_inches="tight", dpi=150)
    plt.close()
    temp_charts = [bar_chart_path]

    # 4. Executive Summary (example text)
    summary_text = (
        f"Total positive variance: ${key_metrics['Total Variance'].sum():,.2f}. "
        f"Top item: {key_metrics.loc[key_metrics['Total Variance'].idxmax(), 'CAReport Name']}."
    )

    # 5. Build PDF with ReportLab
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    if os.path.exists(LOGO_PATH):
        elements.append(Image(LOGO_PATH, width=180, height=60))
        elements.append(Spacer(1, 12))

    elements.append(Paragraph(REPORT_TITLE, styles["Title"]))
    elements.append(Paragraph("Amsurg QA Results", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    metrics_data = [
        ["Total Points", "Matches", "Mismatches"],
        [str(total_points), str(match_count), str(mismatch_count)],
    ]
    metrics_table = Table(metrics_data)
    metrics_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(BRAND_BLUE)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ]
        )
    )
    elements.append(metrics_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(summary_text, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Horizontal bar chart of top absolute variances
    elements.append(Image(bar_chart_path, width=400, height=250))
    elements.append(Spacer(1, 12))

    # Key metrics table
    km_table = Table(dataframe_to_table(key_metrics))
    km_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(BRAND_BLUE)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(km_table)
    elements.append(Spacer(1, 12))


    doc.build(elements)

    # Clean up temporary chart images
    for chart in temp_charts:
        if os.path.exists(chart):
            os.remove(chart)

    print(f"PDF report generated: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
