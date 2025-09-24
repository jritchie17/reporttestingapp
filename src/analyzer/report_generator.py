"""Utilities for building text and HTML comparison reports."""

from typing import Dict, Iterable, Optional
import pandas as pd


def _build_summary_lines(
    sheet_name: str,
    comparison_results: Dict,
    sign_flip_accounts: Iterable[str] = None,
    suggested_accounts: Iterable[str] = None,
    mismatches_df: Optional[pd.DataFrame] = None,
) -> list:
    """Return a list of markdown formatted lines summarising results."""

    lines = [f"# Comparison Report: {sheet_name}", ""]
    mismatch_pct = comparison_results.get("summary", {}).get("mismatch_percentage", 0)
    if mismatch_pct == 0:
        status = "✅ PERFECT MATCH"
    elif mismatch_pct < 1:
        status = "✅ GOOD MATCH"
    elif mismatch_pct < 5:
        status = "⚠️ MODERATE MISMATCH"
    else:
        status = "❌ SIGNIFICANT MISMATCH"
    lines.append(f"**Status:** {status}")
    lines.append("")
    lines.append(
        f"**Match Rate:** {100 - mismatch_pct:.2f}% ("
        f"{comparison_results['summary']['matching_cells']} of {comparison_results['summary']['total_cells']} cells match)"
    )
    lines.append("")
    lines.append("## Data Coverage")
    lines.append("")
    lines.append(f"**Excel Records:** {comparison_results['row_counts']['excel']}")
    lines.append(f"**SQL Records:** {comparison_results['row_counts']['sql']}")
    lines.append(f"**Matched Records:** {comparison_results['row_counts']['matched']}")
    if sign_flip_accounts:
        lines.append("")
        lines.append("**Sign Flip Accounts Applied:** " + ", ".join(sorted(sign_flip_accounts)))
    if suggested_accounts:
        lines.append("")
        lines.append("**Suggested Sign Flip Accounts:** " + ", ".join(sorted(suggested_accounts)))

    column_comparisons = comparison_results.get("column_comparisons", {})
    if column_comparisons:
        lines.append("")
        lines.append("## Per-Column Mismatches")
        for col, stats in column_comparisons.items():
            lines.append(f"- {col}: {stats.get('mismatch_count', 0)} mismatches")

    if mismatches_df is not None and not mismatches_df.empty:
        missing_rows = mismatches_df[mismatches_df["Result"].isin(["Missing in Excel", "Missing in Database"])]
        if not missing_rows.empty:
            lines.append("")
            lines.append("## Missing Rows")
            for _, row in missing_rows.iterrows():
                center = row.get("Center", "")
                acct = row.get("CAReport Name", "")
                result = row.get("Result", "")
                lines.append(f"- {center} {acct} ({result})")

    return lines


def _df_to_markdown(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except (ImportError, ModuleNotFoundError):
        return df.to_string(index=False)


def _df_to_html(df: pd.DataFrame) -> str:
    return df.to_html(index=False, border=0)


def generate_report(
    sheet_name: str,
    comparison_results: Dict,
    mismatches_df: Optional[pd.DataFrame] = None,
    sign_flip_accounts: Iterable[str] = None,
    suggested_accounts: Iterable[str] = None,
    fmt: str = "markdown",
) -> str:
    """Return a report string in the desired format."""

    base_lines = _build_summary_lines(
        sheet_name,
        comparison_results,
        sign_flip_accounts,
        suggested_accounts,
        mismatches_df,
    )

    mismatch_table = (
        mismatches_df[mismatches_df["Result"] != "Match"] if mismatches_df is not None else pd.DataFrame()
    )

    if fmt == "markdown":
        lines = list(base_lines)
        lines.append("")
        lines.append("## Mismatches")
        if mismatch_table.empty:
            lines.append("No mismatches found.")
        else:
            lines.append(_df_to_markdown(mismatch_table))
        return "\n".join(lines)

    if fmt == "html":
        html_lines = list(base_lines)
        html_lines.append("")
        html_lines.append("## Mismatches")
        if mismatch_table.empty:
            html_lines.append("No mismatches found.")
        html_parts = []
        list_open = False
        for ln in html_lines:
            if ln.startswith("# "):
                if list_open:
                    html_parts.append("</ul>")
                    list_open = False
                html_parts.append(f"<h1>{ln[2:]}</h1>")
            elif ln.startswith("## "):
                if list_open:
                    html_parts.append("</ul>")
                    list_open = False
                html_parts.append(f"<h2>{ln[3:]}</h2>")
            elif ln.startswith("- "):
                if not list_open:
                    html_parts.append("<ul>")
                    list_open = True
                html_parts.append(f"<li>{ln[2:]}</li>")
            else:
                if list_open:
                    html_parts.append("</ul>")
                    list_open = False
                html_parts.append(f"<p>{ln}</p>")
        if list_open:
            html_parts.append("</ul>")
        if not mismatch_table.empty:
            html_parts.append(_df_to_html(mismatch_table))
        return "\n".join(html_parts)

    raise ValueError("Unknown format: " + fmt)


def export_markdown(
    sheet_name: str,
    comparison_results: Dict,
    mismatches_df: Optional[pd.DataFrame] = None,
    sign_flip_accounts: Iterable[str] = None,
    suggested_accounts: Iterable[str] = None,
) -> str:
    """Convenience wrapper to return a markdown report."""

    return generate_report(
        sheet_name,
        comparison_results,
        mismatches_df,
        sign_flip_accounts,
        suggested_accounts,
        fmt="markdown",
    )


def export_html(
    sheet_name: str,
    comparison_results: Dict,
    mismatches_df: Optional[pd.DataFrame] = None,
    sign_flip_accounts: Iterable[str] = None,
    suggested_accounts: Iterable[str] = None,
) -> str:
    """Convenience wrapper to return an HTML report."""

    return generate_report(
        sheet_name,
        comparison_results,
        mismatches_df,
        sign_flip_accounts,
        suggested_accounts,
        fmt="html",
    )
