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


def _generate_donut(match: int, mismatch: int) -> str:
    fig, ax = plt.subplots(figsize=(3, 3))
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
    total_points = len(df)
    total_matches = df["Result"].isin(["Match", "Missing in Excel", "Missing in Database"]).sum()
    total_mismatches = (df["Result"] == "Does Not Match").sum()
    mismatch_df = df[df["Result"] == "Does Not Match"]
    img_data = _generate_donut(total_matches, total_mismatches)

    notes_html = ""
    if TESTING_NOTES_PATH and os.path.exists(TESTING_NOTES_PATH):
        with open(TESTING_NOTES_PATH, "r", encoding="utf-8") as f:
            notes_text = f.read().strip()
        if notes_text:
            formatted = notes_text.replace("\n", "<br>")
            notes_html = f"<h2>Testing Notes</h2><p>{formatted}</p>"

    table_headers = "".join(f"<th>{h}</th>" for h in mismatch_df.columns)
    table_rows = "".join(
        "<tr>" + "".join(
            f"<td>{{val}}</td>".format(val=str(row[col])) for col in mismatch_df.columns
        ) + "</tr>" for _, row in mismatch_df.iterrows()
    )

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset='UTF-8'>
<title>{REPORT_TITLE}</title>
<style>
body {{ font-family: Arial, sans-serif; color: {BRAND_BLUE}; margin: 20px; }}
.container {{ max-width: 750px; margin:auto; }}
.cards {{ display:flex; justify-content: space-between; margin-bottom:20px; }}
.card {{ flex:1; background:#f5f5f5; border-radius:6px; padding:10px; margin:0 5px; text-align:center; }}
.card-value {{ font-size:20px; font-weight:bold; }}
.chart {{ text-align:center; margin-bottom:20px; }}
.table-container {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; }}
th, td {{ border:1px solid #ddd; padding:4px; max-width:150px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
th {{ background:{BRAND_BLUE}; color:white; }}
tr:nth-child(even) {{ background:#f9f9f9; }}
</style>
</head>
<body>
<div class='container'>
<h1>{REPORT_TITLE}</h1>
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
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML report generated: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()

