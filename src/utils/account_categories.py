"""Utilities for aggregating SQL results by account category."""

from __future__ import annotations

from typing import Dict, Iterable, List, Any


class CategoryCalculator:
    """Compute category totals and evaluate formulas."""

    def __init__(
        self,
        categories: Dict[str, Iterable[str]] | None = None,
        formulas: Dict[str, str] | None = None,
        account_column: str = "CAReportName",
    ) -> None:
        self.categories = {k: list(v) for k, v in (categories or {}).items()}
        self.formulas = formulas or {}
        self.account_column = account_column

    def _numeric_columns(self, rows: List[Dict[str, Any]]) -> List[str]:
        """Return the names of numeric columns in the result set."""
        numeric_cols: List[str] = []
        for row in rows:
            for key, val in row.items():
                if isinstance(val, (int, float)) and key not in numeric_cols:
                    numeric_cols.append(key)
            if numeric_cols:
                break
        return numeric_cols

    def compute(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return rows extended with category totals and formula rows."""
        if not rows:
            return []

        result = list(rows)
        numeric_cols = self._numeric_columns(rows)
        totals: Dict[str, Dict[str, float]] = {}

        for name, accounts in self.categories.items():
            totals[name] = {col: 0.0 for col in numeric_cols}
            for row in rows:
                acct = str(row.get(self.account_column, ""))
                if acct in accounts:
                    for col in numeric_cols:
                        val = row.get(col)
                        if isinstance(val, (int, float)):
                            totals[name][col] += float(val)
            result.append({self.account_column: name, **totals[name]})

        for form_name, expr in self.formulas.items():
            values = {}
            for col in numeric_cols:
                local = {k: totals.get(k, {}).get(col, 0.0) for k in self.categories}
                try:
                    values[col] = eval(expr, {}, local)
                except Exception:
                    values[col] = None
            result.append({self.account_column: form_name, **values})

        return result
