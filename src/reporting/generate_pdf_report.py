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

    # Calculate basic counts
    total_points = len(df)
    match_count = (df["Result"] == "Match").sum()
    mismatch_df = df[df["Result"] != "Match"]
    mismatch_count = len(mismatch_df)

    # Pie chart showing match vs mismatch counts using brand colors
    plt.figure(figsize=(3, 3))
    pie_path = os.path.join(BASE_DIR, "match_vs_mismatch.png")
    plt.pie(
        [match_count, mismatch_count],
        labels=["Match", "Mismatch"],
        colors=["#76A240", "#F58025"],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"width": 0.4},
    )
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(pie_path, bbox_inches="tight", dpi=150)
    plt.close()

    # Use only mismatches for the report
    df = mismatch_df

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
    elements.append(Paragraph("Amsurg QA Results", styles["Heading2"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Total Points: {total_points}", styles["Normal"]))
    elements.append(Paragraph(f"Matches: {match_count}", styles["Normal"]))
    elements.append(Paragraph(f"Mismatches: {mismatch_count}", styles["Normal"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(summary_text, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Pie chart image before tables
    elements.append(Image(pie_path, width=200, height=200))
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

    # Variance chart image
    elements.append(Image(chart_path, width=400, height=250))
    elements.append(Spacer(1, 12))

    # Detailed results table
    detail_table = Table(dataframe_to_table(df), repeatRows=1)
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
