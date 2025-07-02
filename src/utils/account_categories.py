"""Utilities for aggregating SQL results by account category."""

from __future__ import annotations

from typing import Dict, Iterable, List, Any
from decimal import Decimal
import re
from .account_patterns import ACCOUNT_PATTERNS

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

        # Map original category names to safe Python identifiers for formula evaluation
        self._safe_names: Dict[str, str] = {}
        for idx, name in enumerate(self.categories):
            safe = re.sub(r"\W|^(?=\d)", "_", name)
            if not safe or safe in self._safe_names.values():
                safe = f"cat_{idx}"
            self._safe_names[name] = safe

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

        for pat in ACCOUNT_PATTERNS:
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

        # Identify account numbers referenced directly in formulas
        account_refs = set()
        for expr in self.formulas.values():
            for pat in ACCOUNT_PATTERNS:
                for match in re.findall(pat, expr):
                    account_refs.add(match)

        # Create local mapping of safe names including referenced accounts
        safe_names = dict(self._safe_names)
        for acct in account_refs:
            if acct not in safe_names:
                safe = re.sub(r"\W|^(?=\d)", "_", acct)
                if not safe or safe in safe_names.values():
                    base = "acct"
                    idx = 0
                    new_safe = base
                    while new_safe in safe_names.values():
                        idx += 1
                        new_safe = f"{base}_{idx}"
                    safe = new_safe
                safe_names[acct] = safe

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

        account_totals: Dict[Any, Dict[str, Dict[str, Decimal]]] = {
            g: {
                acc: {col: Decimal("0") for col in numeric_cols}
                for acc in account_refs
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
                    elif not acct_code and not cat_code:
                        if acct_raw.strip().lower() == str(acc).strip().lower():
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

            for acc in account_refs:
                acc_code = self._extract_account_code(acc)
                if acct_code and acc_code and acct_code == acc_code:
                    for col in numeric_cols:
                        val = row.get(col)
                        if isinstance(val, (int, float, Decimal)) and not isinstance(val, bool):
                            if sign_flip.should_flip(acct_raw, self.sign_flip_accounts):
                                val = -val
                            if isinstance(val, Decimal):
                                account_totals[group_val][acc][col] += val
                            else:
                                account_totals[group_val][acc][col] += Decimal(str(val))
                    break

        for g in groups:
            for name in self.categories:
                row_vals = {account_col: name, **totals[g][name]}
                if group_exists:
                    row_vals[self.group_column] = g
                result.append(row_vals)

            for form_name, expr in self.formulas.items():
                # Replace category names and account refs with safe identifiers
                safe_expr = expr
                for name, safe in sorted(
                    safe_names.items(), key=lambda x: len(x[0]), reverse=True
                ):
                    safe_expr = re.sub(r"\b" + re.escape(name) + r"\b", safe, safe_expr)

                values = {}
                for col in numeric_cols:
                    local = {
                        safe_names[k]: totals[g].get(k, {}).get(col, Decimal("0"))
                        for k in self.categories
                    }
                    for acc in account_refs:
                        local[safe_names[acc]] = account_totals[g].get(acc, {}).get(col, Decimal("0"))
                    try:
                        values[col] = eval(safe_expr, {}, local)
                    except Exception:
                        values[col] = None
                row_vals = {account_col: form_name, **values}
                if group_exists:
                    row_vals[self.group_column] = g
                result.append(row_vals)

        return result
