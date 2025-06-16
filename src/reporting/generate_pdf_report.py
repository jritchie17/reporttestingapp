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
    """Generate a concise QA report PDF."""
    # 1. Load Data
    df = pd.read_csv(RESULTS_CSV)

    total_points = len(df)
    match_count = int((df["Result"] == "Match").sum())
    mismatch_df = df[df["Result"] != "Match"]
    mismatch_count = total_points - match_count

    # 2. Summary table of mismatched accounts
    mismatch_summary = (
        mismatch_df["CAReport Name"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "CAReport Name", "CAReport Name": "Mismatch Count"})
    )

    # 3. Generate Visuals
    plt.figure(figsize=(3, 3))
    plt.pie([match_count, mismatch_count], labels=["Match", "Mismatch"], autopct="%1.0f%%")
    pie_chart = os.path.join(BASE_DIR, "match_pie_chart.png")
    plt.savefig(pie_chart, bbox_inches="tight", dpi=150)
    plt.close()

    plt.figure(figsize=(6, 3))
    mismatch_summary.head(10).plot(
        kind="bar",
        x="CAReport Name",
        y="Mismatch Count",
        legend=False,
        color="firebrick",
    )
    plt.title("Top Mismatched Accounts")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    bar_chart = os.path.join(BASE_DIR, "mismatch_by_careportname.png")
    plt.savefig(bar_chart, bbox_inches="tight", dpi=150)
    plt.close()

    # 4. Build PDF with ReportLab
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    if os.path.exists(LOGO_PATH):
        elements.append(Image(LOGO_PATH, width=180, height=60))
        elements.append(Spacer(1, 12))

    elements.append(Paragraph(REPORT_TITLE, styles["Title"]))
    elements.append(Paragraph("Amsurg QA Results", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    summary_text = (
        f"Total data points tested: {total_points:,}<br/>"
        f"Matching data points: {match_count:,}<br/>"
        f"Mismatched data points: {mismatch_count:,}"
    )
    elements.append(Paragraph(summary_text, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Charts
    elements.append(Image(pie_chart, width=180, height=180))
    elements.append(Spacer(1, 12))
    elements.append(Image(bar_chart, width=400, height=200))
    elements.append(Spacer(1, 12))

    # Mismatch summary table
    mismatch_table = Table(dataframe_to_table(mismatch_summary))
    mismatch_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2a4d69")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    elements.append(mismatch_table)

    doc.build(elements)

    print(f"PDF report generated: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
