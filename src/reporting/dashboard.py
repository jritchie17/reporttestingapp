import os
import pandas as pd
from flask import Flask
from dash import Dash, dcc, html
import plotly.express as px


DEFAULT_CSV = os.path.join(os.path.dirname(__file__), "results.csv")


def load_results(csv_path: str = DEFAULT_CSV) -> pd.DataFrame:
    """Load comparison results from a CSV file."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Results file not found: {csv_path}")
    return pd.read_csv(csv_path)


def find_sign_flip_suggestions(df: pd.DataFrame) -> set:
    """Infer sign flip candidates from the results dataframe."""
    suggestions = set()
    acct_col = None
    for c in ["CAReport Name", "CAReportName", "Account", "Account Number"]:
        if c in df.columns:
            acct_col = c
            break
    if acct_col and "Excel Value" in df.columns and "DataBase Value" in df.columns:
        for _, row in df.iterrows():
            try:
                excel_val = float(row["Excel Value"])
                db_val = float(row["DataBase Value"])
                if excel_val == -db_val:
                    suggestions.add(str(row[acct_col]))
            except Exception:
                continue
    return suggestions


def create_app(df: pd.DataFrame, suggestions: set) -> Flask:
    """Create the Flask/Dash dashboard app."""
    server = Flask(__name__)
    app = Dash(__name__, server=server, url_base_pathname="/")

    counts = df["Result"].value_counts().reset_index()
    counts.columns = ["Result", "Count"]
    fig_results = px.bar(counts, x="Result", y="Count", title="Result Counts")

    if "Variance" in df.columns and "CAReport Name" in df.columns:
        var_df = df.groupby("CAReport Name")["Variance"].sum().abs().reset_index()
        var_df = var_df.sort_values("Variance", ascending=False).head(10)
        fig_variance = px.bar(var_df, x="CAReport Name", y="Variance",
                              title="Top Variances by Account")
    else:
        fig_variance = None

    app.layout = html.Div([
        html.H1("Comparison Dashboard"),
        dcc.Graph(figure=fig_results),
        dcc.Graph(figure=fig_variance) if fig_variance else html.Div(),
        html.H2("Suggested Sign-Flip Accounts"),
        html.Ul([html.Li(a) for a in sorted(suggestions)]) if suggestions else html.P("None")
    ])

    return server


def run_dashboard(csv_path: str = DEFAULT_CSV):
    df = load_results(csv_path)
    suggestions = find_sign_flip_suggestions(df)
    server = create_app(df, suggestions)
    server.run(debug=True)


if __name__ == "__main__":
    run_dashboard()
