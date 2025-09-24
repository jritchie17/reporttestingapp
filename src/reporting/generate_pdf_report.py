import os
from typing import List
import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Template

# Brand color palette
BRAND_BLUE = "#004B8D"
BRAND_BLUE_LIGHT = "#E6EEF5"
BRAND_BLUE_DARK = "#003366"
LIGHT_GRAY = "#F8F9FA"
DARK_GRAY = "#343A40"
ACCENT_GRAY = "#E9ECEF"
TEXT_GRAY = "#495057"

# CONFIGURATION
REPORT_TITLE = os.getenv("REPORT_TITLE", "SOO Preclose Financial Report")
# Resolve paths relative to this file so it works regardless of the current
# working directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")  # Place your company logo here
RESULTS_CSV = os.path.join(BASE_DIR, "results.csv")  # Path to your results data
OUTPUT_HTML = os.path.join(BASE_DIR, "SOO_Preclose_Report.html")


def truncate_text(text: str, max_length: int = 30) -> str:
    """Truncate text and add ellipsis if it exceeds max_length."""
    return text if len(str(text)) <= max_length else str(text)[:max_length-3] + "..."


def format_mismatch_value(value) -> str:
    """Format mismatch table values, falling back to the original text when not numeric."""
    if pd.isna(value) or value is None:
        return "N/A"

    value_str = str(value).strip()
    if value_str == "":
        return "N/A"

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        # Try again after removing common currency formatting characters
        cleaned = value_str.replace(",", "").replace("$", "")
        try:
            numeric_value = float(cleaned)
        except (TypeError, ValueError):
            return truncate_text(value_str, 30)
    return f"${numeric_value:,.2f}"


def create_modern_pie_chart(match_count: int, mismatch_count: int) -> str:
    plt.style.use('default')  # Use default style instead of seaborn
    fig, ax = plt.subplots(figsize=(4, 4))
    
    # Create pie chart with modern styling
    wedges, texts, autotexts = ax.pie(
        [match_count, mismatch_count],
        labels=['Matches', 'Mismatches'],
        colors=[BRAND_BLUE, BRAND_BLUE_LIGHT],
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    
    # Style the text
    plt.setp(autotexts, size=10, weight="bold", color="white")
    plt.setp(texts, size=10, weight="bold", color=TEXT_GRAY)
    
    # Add a white circle in the middle for a donut effect
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    
    # Remove background
    ax.set_facecolor('none')
    fig.patch.set_facecolor('none')
    
    plt.axis('equal')
    chart_path = os.path.join(BASE_DIR, "match_pie_chart.png")
    plt.savefig(chart_path, bbox_inches="tight", dpi=150, transparent=True)
    plt.close()
    return chart_path


def main() -> None:
    # Load and process data
    df = pd.read_csv(RESULTS_CSV)
    total_points = len(df)
    
    # Count matches and mismatches
    # Consider 'Missing in Excel' and 'Missing in Database' as matches
    match_count = len(df[df["Result"].isin(["Match", "Missing in Excel", "Missing in Database"])])
    mismatch_count = len(df[df["Result"] == "Does Not Match"])
    
    # Filter for mismatches only
    mismatch_df = df[df["Result"] == "Does Not Match"]
    
    # Create modern pie chart
    pie_chart_path = create_modern_pie_chart(match_count, mismatch_count)

    # Prepare table data
    table_data = []
    for _, row in mismatch_df.iterrows():
        table_data.append({
            'field': truncate_text(row["Field"], 15),
            'report_name': truncate_text(row["CAReport Name"], 25),
            'variance': format_mismatch_value(row['Variance']),
            'excel_value': format_mismatch_value(row['Excel Value']),
            'db_value': format_mismatch_value(row['DataBase Value'])
        })
    
    # HTML template with modern styling
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{{ title }}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            @media print {
                @page {
                    size: letter;
                    margin: 0.5in;
                }
                body {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }
            }
            
            body {
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 2rem;
                color: #343A40;
                background: white;
            }
            
            .header {
                display: flex;
                align-items: center;
                margin-bottom: 2rem;
            }
            
            .logo {
                max-height: 60px;
                margin-right: 2rem;
            }
            
            .title {
                color: #004B8D;
                font-size: 28px;
                font-weight: 700;
                margin: 0;
            }
            
            .metrics-container {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .metric-card {
                background: #F8F9FA;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                border-top: 4px solid #004B8D;
                transition: transform 0.2s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            
            .metric-title {
                color: #004B8D;
                font-size: 14px;
                font-weight: 600;
                margin: 0 0 0.5rem 0;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .metric-value {
                font-size: 24px;
                font-weight: 700;
                margin: 0;
                color: #343A40;
            }
            
            .chart-container {
                text-align: center;
                margin: 2rem 0;
                padding: 1rem;
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            .chart {
                max-width: 300px;
                margin: 0 auto;
            }
            
            .table-container {
                margin-top: 2rem;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
            }
            
            th {
                background: #004B8D;
                color: white;
                font-weight: 600;
                text-align: left;
                padding: 1rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 12px;
            }
            
            td {
                padding: 1rem;
                border-bottom: 1px solid #E9ECEF;
            }
            
            tr:nth-child(even) {
                background: #F8F9FA;
            }
            
            tr:hover {
                background: #E6EEF5;
            }
            
            .number-cell {
                text-align: right;
                font-family: 'Inter', monospace;
                font-weight: 500;
            }
            
            .print-instructions {
                position: fixed;
                bottom: 1rem;
                right: 1rem;
                background: #004B8D;
                color: white;
                padding: 1rem;
                border-radius: 8px;
                font-size: 14px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                display: none;
            }
            
            @media print {
                .print-instructions {
                    display: none !important;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            {% if logo_exists %}
            <img src="{{ logo_path }}" class="logo" alt="Logo">
            {% endif %}
            <h1 class="title">{{ title }}</h1>
        </div>
        
        <div class="metrics-container">
            <div class="metric-card">
                <h3 class="metric-title">Total Points</h3>
                <p class="metric-value">{{ total_points }}</p>
            </div>
            <div class="metric-card">
                <h3 class="metric-title">Matches</h3>
                <p class="metric-value">{{ match_count }}</p>
            </div>
            <div class="metric-card">
                <h3 class="metric-title">Mismatches</h3>
                <p class="metric-value">{{ mismatch_count }}</p>
            </div>
        </div>
        
        <div class="chart-container">
            <img src="{{ chart_path }}" class="chart" alt="Match Distribution">
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Field</th>
                        <th>CAReport Name</th>
                        <th>Variance</th>
                        <th>Excel Value</th>
                        <th>Database Value</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in table_data %}
                    <tr>
                        <td>{{ row.field }}</td>
                        <td>{{ row.report_name }}</td>
                        <td class="number-cell">{{ row.variance }}</td>
                        <td class="number-cell">{{ row.excel_value }}</td>
                        <td class="number-cell">{{ row.db_value }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="print-instructions">
            To save as PDF: Press Ctrl+P (or Cmd+P on Mac) and select "Microsoft Print to PDF" as your printer
        </div>
    </body>
    </html>
    """
    
    # Render HTML
    template = Template(html_template)

    # Use paths relative to the HTML output so the report works on any machine
    output_dir = os.path.dirname(OUTPUT_HTML)
    relative_logo_path = os.path.relpath(LOGO_PATH, start=output_dir)
    relative_chart_path = os.path.relpath(pie_chart_path, start=output_dir)

    html_content = template.render(
        title=REPORT_TITLE,
        logo_exists=os.path.exists(LOGO_PATH),
        logo_path=relative_logo_path,
        total_points=total_points,
        match_count=match_count,
        mismatch_count=mismatch_count,
        chart_path=relative_chart_path,
        table_data=table_data
    )
    
    # Save HTML file
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"HTML report generated: {OUTPUT_HTML}")
    print("Open this file in your browser and use Ctrl+P to save as PDF")


if __name__ == "__main__":
    main()
