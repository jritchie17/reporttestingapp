"""Utilities for aggregating SQL results by account category."""

from __future__ import annotations

from typing import Dict, Iterable, List, Any
from decimal import Decimal
import re

from src.analyzer import sign_flip


class CategoryCalculator:
    """Compute category totals and evaluate formulas."""

    def __init__(
        self,
        categories: Dict[str, Iterable[str]] | None = None,
        formulas: Dict[str, str] | None = None,
        account_column: str = "CAReportName",
        group_column: str | None = "Center",
        sign_flip_accounts: Iterable[str] | None = None,
    ) -> None:
        """Create a new calculator.

        Parameters
        ----------
        categories:
            Mapping of category name to a collection of account numbers.
        formulas:
            Optional mapping of formula name to a Python expression using the
            category names as variables.
        account_column:
            Name of the column containing the account identifier in ``rows``.
        group_column:
            Optional column name used to group rows before aggregating.  If this
            column is present in the input rows, totals and formulas are
            computed separately for each unique value.
        sign_flip_accounts:
            Collection of account identifiers whose numeric values should be
            multiplied by ``-1`` before aggregation.
        """

        self.categories = {k: list(v) for k, v in (categories or {}).items()}
        self.formulas = formulas or {}
        self.account_column = account_column
        self.group_column = group_column
        self.sign_flip_accounts = {str(a).strip() for a in sign_flip_accounts or []}

    def _resolve_account_column(self, rows: List[Dict[str, Any]]) -> str:
        """Return a suitable account column name for the given rows."""
        if rows and self.account_column in rows[0]:
            return self.account_column

        candidates = [
            "CAReportName",
            "Account",
            "Account Number",
            "AccountNumber",
            "Acct",
        ]
        if rows:
            first_row = rows[0]
            for cand in candidates:
                if cand in first_row:
                    return cand
            for key in first_row:
                if "account" in str(key).lower():
                    return key
        return self.account_column

    def _numeric_columns(self, rows: List[Dict[str, Any]]) -> List[str]:
        """Return the names of numeric columns in the result set."""
        numeric_cols: List[str] = []
        for row in rows:
            for key, val in row.items():
                if key == self.group_column:
                    # never treat the grouping column as numeric
                    continue
                if isinstance(val, (int, float, Decimal)) and not isinstance(val, bool):
                    if key not in numeric_cols:
                        numeric_cols.append(key)
        if self.group_column and self.group_column in numeric_cols:
            numeric_cols.remove(self.group_column)
        return numeric_cols

    @staticmethod
    def _extract_account_code(text: str) -> str:
        """Return a normalized account identifier from ``text``.

        The method searches for common account patterns (with or without a
        dash) and returns only the digits found. If no pattern is detected,
        an empty string is returned.
        """

        if not text:
            return ""

        patterns = [
            r"(\d{4}-?\d{4})",
            r"(\d{5}-?\d{3})",
            r"(\d{3}-?\d{5})",
            r"(\d{4}-?\d{5})",
            r"(\d{7,8})",
        ]

        for pat in patterns:
            match = re.search(pat, str(text))
            if match:
                return match.group(1).replace("-", "")

        return ""

    def compute(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return rows extended with category totals and formula rows.

        If ``group_column`` was supplied and is present in the data, totals are
        calculated separately for each value of that column and the resulting
        rows include the grouping value.
        """
        if not rows:
            return []

        account_col = self._resolve_account_column(rows)

        result = list(rows)
        numeric_cols = self._numeric_columns(rows)

        group_exists = bool(self.group_column and self.group_column in rows[0])
        if group_exists:
            groups = sorted({row[self.group_column] for row in rows})
        else:
            groups = [None]

        totals: Dict[Any, Dict[str, Dict[str, Decimal]]] = {
            g: {
                name: {col: Decimal("0") for col in numeric_cols}
                for name in self.categories
            }
            for g in groups
        }

        for row in rows:
            group_val = row.get(self.group_column) if group_exists else None
            acct_raw = str(row.get(account_col, ""))
            acct_code = self._extract_account_code(acct_raw)
            for name, accounts in self.categories.items():
                for acc in accounts:
                    cat_code = self._extract_account_code(acc)
                    if acct_code and cat_code and acct_code == cat_code:
                        for col in numeric_cols:
                            val = row.get(col)
                            if isinstance(
                                val, (int, float, Decimal)
                            ) and not isinstance(val, bool):
                                if sign_flip.should_flip(
                                    acct_raw, self.sign_flip_accounts
                                ):
                                    val = -val
                                if isinstance(val, Decimal):
                                    totals[group_val][name][col] += val
                                else:
                                    totals[group_val][name][col] += Decimal(str(val))
                        break

        for g in groups:
            for name in self.categories:
                row_vals = {account_col: name, **totals[g][name]}
                if group_exists:
                    row_vals[self.group_column] = g
                result.append(row_vals)

            for form_name, expr in self.formulas.items():
                values = {}
                for col in numeric_cols:
                    local = {
                        k: totals[g].get(k, {}).get(col, Decimal("0"))
                        for k in self.categories
                    }
                    try:
                        values[col] = eval(expr, {}, local)
                    except Exception:
                        values[col] = None
                row_vals = {account_col: form_name, **values}
                if group_exists:
                    row_vals[self.group_column] = g
                result.append(row_vals)

        return result
