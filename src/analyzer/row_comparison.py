from typing import Iterable, Any
import pandas as pd

from . import sign_flip


def compare_series(excel_series: Iterable[Any], sql_series: Iterable[Any], account_series: Iterable[Any] = None,
                   tolerance: float = 0.001, sign_flip_accounts: Iterable[str] = None):
    """Compare two series and return statistics used by the comparison engine."""
    if account_series is None:
        account_series = [None] * len(list(excel_series))
    excel_series = pd.Series(excel_series).reset_index(drop=True)
    sql_series = pd.Series(sql_series).reset_index(drop=True)
    account_series = pd.Series(account_series).reset_index(drop=True)

    results = {
        "is_numeric": False,
        "match_count": 0,
        "mismatch_count": 0,
        "mismatch_rows": [],
        "null_mismatch_count": 0,
        "sign_flipped": bool(sign_flip_accounts),
        "sign_flip_candidates": set(),
    }

    try:
        excel_num = pd.to_numeric(excel_series, errors="coerce")
        sql_num = pd.to_numeric(sql_series, errors="coerce")
        if excel_num.notna().mean() > 0.5 and sql_num.notna().mean() > 0.5:
            results["is_numeric"] = True
            excel_series = excel_num
            sql_series = sql_num
    except Exception:
        pass

    for i, (e_val, s_val, acct) in enumerate(zip(excel_series, sql_series, account_series)):
        e_null = pd.isna(e_val)
        s_null = pd.isna(s_val)
        s_val_adj = sign_flip.apply(s_val, acct, sign_flip_accounts) if results["is_numeric"] else s_val
        if e_null and s_null:
            results["match_count"] += 1
            continue
        if e_null != s_null:
            treated_as_match = False
            if results["is_numeric"]:
                # Treat NULL on one side and numeric zero on the other as a match
                try:
                    if (e_null and float(s_val_adj) == 0) or (s_null and float(e_val) == 0):
                        results["match_count"] += 1
                        treated_as_match = True
                except Exception:
                    pass
            if not treated_as_match:
                results["null_mismatch_count"] += 1
                results["mismatch_count"] += 1
                results["mismatch_rows"].append({"row": i, "excel_value": e_val, "sql_value": s_val_adj, "difference": "NULL mismatch"})
            continue
        if results["is_numeric"]:
            try:
                e_num = float(e_val)
                s_num = float(s_val_adj)
                diff = abs(e_num - s_num)
                if (abs(e_num) > 1 or abs(s_num) > 1):
                    max_val = max(abs(e_num), abs(s_num))
                    match = diff / max_val <= tolerance
                else:
                    max_val = 1
                    match = diff <= tolerance
                if match:
                    results["match_count"] += 1
                else:
                    results["mismatch_count"] += 1
                    results["mismatch_rows"].append({"row": i, "excel_value": e_val, "sql_value": s_val_adj, "difference": e_num - s_num})
                    # Check if flipping sign would produce a match
                    try:
                        if not sign_flip.should_flip(acct, sign_flip_accounts):
                            s_orig = float(s_val)
                            diff_flip = abs(e_num + s_orig)
                            flip_match = diff_flip / max_val <= tolerance if max_val != 1 else diff_flip <= tolerance
                            if flip_match:
                                results["sign_flip_candidates"].add(sign_flip._normalize_account(acct))
                    except Exception:
                        pass
            except Exception:
                if str(e_val).strip() == str(s_val_adj).strip():
                    results["match_count"] += 1
                else:
                    results["mismatch_count"] += 1
                    results["mismatch_rows"].append({"row": i, "excel_value": e_val, "sql_value": s_val_adj, "difference": "String mismatch"})
        else:
            if str(e_val).strip().lower() == str(s_val_adj).strip().lower():
                results["match_count"] += 1
            else:
                results["mismatch_count"] += 1
                results["mismatch_rows"].append({"row": i, "excel_value": e_val, "sql_value": s_val_adj, "difference": "String mismatch"})

    total = results["match_count"] + results["mismatch_count"]
    results["match_percentage"] = (results["match_count"] / total * 100) if total else 0
    return results
