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

    # 2. Generate Key Metrics Table
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

    # 3. Generate Visuals
    plt.figure(figsize=(8, 4))
    key_metrics.plot(
        kind="bar",
        x="CAReport Name",
        y="Total Variance",
        legend=False,
        color="steelblue",
    )
    plt.title("Variance by CAReport Name")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    chart_path = os.path.join(BASE_DIR, "variance_by_careportname.png")
    plt.savefig(chart_path, bbox_inches="tight", dpi=150)
    plt.close()

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
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(summary_text, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Key metrics table
    km_table = Table(dataframe_to_table(key_metrics))
    km_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2a4d69")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(km_table)
    elements.append(Spacer(1, 12))

    # Chart image
    elements.append(Image(chart_path, width=400, height=250))
    elements.append(Spacer(1, 12))

    # Detailed results table
    # Only show rows where the Result column is not "Match"
    mismatch_df = df[df["Result"] != "Match"]
    detail_table = Table(dataframe_to_table(mismatch_df), repeatRows=1)
    detail_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2a4d69")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(detail_table)

    doc.build(elements)

    print(f"PDF report generated: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
