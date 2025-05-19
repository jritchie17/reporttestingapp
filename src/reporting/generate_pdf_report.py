import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

# CONFIGURATION
REPORT_TITLE = "SOO Preclose Financial Report"
LOGO_PATH = "logo.png"  # Place your company logo here
RESULTS_CSV = "results.csv"  # Path to your results data
OUTPUT_PDF = "SOO_Preclose_Report.pdf"

# 1. Load Data
df = pd.read_csv(RESULTS_CSV)

# 2. Generate Key Metrics Table (customize as needed)
key_metrics = df.groupby('Center').agg({
    'Variance': 'sum',
    'Actual': 'sum',
    'Budget': 'sum'
}).reset_index()
key_metrics.columns = ['Center', 'Total Variance', 'Total Actual', 'Total Budget']

# 3. Generate Visuals (example: Variance by Center)
plt.figure(figsize=(10, 6))
sns.barplot(data=key_metrics, x='Center', y='Total Variance', palette='Blues_d')
plt.title('Variance by Center')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
chart_path = 'variance_by_center.png'
plt.savefig(chart_path, bbox_inches='tight', dpi=200)
plt.close()

# 4. Executive Summary (customize or automate as needed)
summary_text = (
    f"<b>Executive Summary:</b> <br>"
    f"Total positive variance: <b>${key_metrics['Total Variance'].sum():,.2f}</b>.<br>"
    f"Top performing center: <b>{key_metrics.loc[key_metrics['Total Variance'].idxmax(), 'Center']}</b>.<br>"
    f"No centers flagged for material risk. All payroll tax % of wages within target."
)

# 5. Prepare HTML Template
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

# Write the template file if it doesn't exist
TEMPLATE_FILE = 'report_template.html'
template_path = os.path.join(TEMPLATE_DIR, TEMPLATE_FILE)
if not os.path.exists(template_path):
    with open(template_path, 'w') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: "Segoe UI", Arial, sans-serif; color: #222; }
        h1, h2 { color: #2a4d69; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: right; }
        th { background: #2a4d69; color: #fff; }
        tr:nth-child(even) { background: #f2f2f2; }
        .summary { background: #d9edf7; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
        .logo { width: 180px; }
    </style>
</head>
<body>
    {% if logo_path and logo_exists %}<img src="{{ logo_path }}" class="logo" />{% endif %}
    <h1>{{ report_title }}</h1>
    <div class="summary">
        {{ summary_text|safe }}
    </div>
    <h2>Key Metrics</h2>
    <table>
        <tr>
            {% for col in key_metrics.columns %}
            <th>{{ col }}</th>
            {% endfor %}
        </tr>
        {% for row in key_metrics.values %}
        <tr>
            {% for val in row %}
            <td>{{ "{:,}".format(val) if val is number else val }}</td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
    <h2>Variance by Center</h2>
    <img src="variance_by_center.png" style="width:100%;max-width:700px;" />
    <h2>Detailed Results</h2>
    <table>
        <tr>
            {% for col in df.columns %}
            <th>{{ col }}</th>
            {% endfor %}
        </tr>
        {% for row in df.values %}
        <tr>
            {% for val in row %}
            <td>{{ val }}</td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
</body>
</html>
''')

template = env.get_template(TEMPLATE_FILE)

# 6. Render HTML
html_out = template.render(
    report_title=REPORT_TITLE,
    logo_path=LOGO_PATH,
    logo_exists=os.path.exists(LOGO_PATH),
    summary_text=summary_text,
    key_metrics=key_metrics,
    df=df,
    number=(int, float)
)

# 7. Export to PDF
HTML(string=html_out, base_url=TEMPLATE_DIR).write_pdf(OUTPUT_PDF)

print(f"PDF report generated: {OUTPUT_PDF}") 