from typing import Dict, Iterable


def generate_report(sheet_name: str, comparison_results: Dict, sign_flip_accounts: Iterable[str] = None) -> str:
    """Create a simple markdown report summarizing comparison results."""
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
    return "\n".join(lines)
