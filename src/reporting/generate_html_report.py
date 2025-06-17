import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

BRAND_BLUE = "#004B8D"
BRAND_ORANGE = "#F58025"
BRAND_GREEN = "#76A240"

REPORT_TITLE = os.getenv("REPORT_TITLE", "SOO Preclose Financial Report")
TESTING_NOTES_PATH = os.getenv("TESTING_NOTES_PATH")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_CSV = os.path.join(BASE_DIR, "results.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "SOO_Preclose_Report.html")


def _generate_donut(match: int, mismatch: int, size: float = 2.0) -> str:
    fig, ax = plt.subplots(figsize=(size, size))
    ax.pie(
        [match, mismatch],
        colors=[BRAND_GREEN, BRAND_ORANGE],
        startangle=90,
        counterclock=False,
        wedgeprops={"width": 0.5},
    )
    percentage = (match / (match + mismatch)) * 100 if match + mismatch else 0
    ax.text(0, 0, f"{percentage:.1f}%", ha="center", va="center", fontsize=12)
    ax.axis("equal")
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def main() -> None:
    df = pd.read_csv(RESULTS_CSV)
    has_issue = "Issue" in df.columns
    if not has_issue:
        df["Issue"] = ""
    total_points = len(df)
    total_matches = df["Result"].isin(["Match", "Missing in Excel", "Missing in Database"]).sum()
    total_mismatches = (df["Result"] == "Does Not Match").sum()
    mismatch_df = df[df["Result"] == "Does Not Match"]
    table_columns = list(mismatch_df.columns)
    if has_issue and "Issue" not in table_columns:
        table_columns.append("Issue")
    img_data = _generate_donut(total_matches, total_mismatches, size=2.0)

    notes_html = ""
    if TESTING_NOTES_PATH and os.path.exists(TESTING_NOTES_PATH):
        with open(TESTING_NOTES_PATH, "r", encoding="utf-8") as f:
            notes_text = f.read().strip()
        if notes_text:
            formatted = notes_text.replace("\n", "<br>")
            notes_html = f"<h2>Testing Notes</h2><p>{formatted}</p>"

    table_headers = "".join(f"<th>{h}</th>" for h in table_columns)
    table_rows = "".join(
        "<tr>" + "".join(
            f"<td>{str(row.get(col, ''))}</td>" for col in table_columns
        ) + "</tr>" for _, row in mismatch_df.iterrows()
    )

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset='UTF-8'>
    <title>{REPORT_TITLE}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        body {{
            font-family: 'Inter', sans-serif;
            color: {BRAND_BLUE};
            margin: 0;
            padding: 1.5rem;
            background: #fff;
        }}

        .container {{
            max-width: 900px;
            margin: auto;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .metric-card {{
            background: #F8F9FA;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-top: 4px solid {BRAND_BLUE};
            text-align: center;
        }}

        .metric-title {{
            font-size: 14px;
            text-transform: uppercase;
            color: {BRAND_BLUE};
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}

        .metric-value {{
            font-size: 22px;
            font-weight: 600;
            color: {BRAND_BLUE};
        }}

        .chart {{
            text-align: center;
            margin-bottom: 2rem;
        }}

        .table-container {{
            overflow-x: auto;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-radius: 8px;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 14px;
        }}

        th {{
            background: {BRAND_BLUE};
            color: white;
            padding: 0.75rem;
            text-align: left;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        td {{
            padding: 0.5rem;
            border-bottom: 1px solid #E9ECEF;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        tr:nth-child(even) {{
            background: #F8F9FA;
        }}
    </style>
</head>
<body>
<<<<<<< HEAD
<div class='container'>
<h1><center>{REPORT_TITLE} - AMSURG QA Validation</center></h1>
<div class='cards'>
<div class='card'><div>Total Data Points</div><div class='card-value'>{total_points}</div></div>
<div class='card'><div>Total Matches</div><div class='card-value'>{total_matches}</div></div>
<div class='card'><div>Total Mismatches</div><div class='card-value'>{total_mismatches}</div></div>
</div>
<div class='chart'><img src='data:image/png;base64,{img_data}' alt='Match Chart'></div>
{notes_html}
<h2>Mismatches</h2>
<div class='table-container'>
<table>
<tr>{table_headers}</tr>
{table_rows}
</table>
</div>
</div>
=======
    <div class='container'>
        <h1>{REPORT_TITLE}</h1>
        <div class='metrics'>
            <div class='metric-card'>
                <div class='metric-title'>Total Data Points</div>
                <div class='metric-value'>{total_points}</div>
            </div>
            <div class='metric-card'>
                <div class='metric-title'>Total Matches</div>
                <div class='metric-value'>{total_matches}</div>
            </div>
            <div class='metric-card'>
                <div class='metric-title'>Total Mismatches</div>
                <div class='metric-value'>{total_mismatches}</div>
            </div>
        </div>
        <div class='chart'>
            <img src='data:image/png;base64,{img_data}' alt='Match Chart'>
        </div>
        {notes_html}
        <h2>Mismatches</h2>
        <div class='table-container'>
            <table>
                <tr>{table_headers}</tr>
                {table_rows}
            </table>
        </div>
    </div>
>>>>>>> 2cb76d0330411bbe654828b9a4daf278e250fa86
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML report generated: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()

