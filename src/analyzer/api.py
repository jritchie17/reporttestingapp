"""Simplified API for comparing data and generating reports."""
from typing import Iterable, Tuple
import pandas as pd

from .comparison_engine import ComparisonEngine
from .report_generator import generate_report


def compare_and_report(sheet_name: str, excel_df: pd.DataFrame, sql_df: pd.DataFrame,
                        sign_flip_accounts: Iterable[str] = None, tolerance: float = 0.001) -> Tuple[dict, str]:
    engine = ComparisonEngine()
    engine.set_tolerance(tolerance)
    engine.set_sign_flip_accounts(sign_flip_accounts)
    results = engine.compare_dataframes(excel_df, sql_df)
    report = generate_report(sheet_name, results, sign_flip_accounts)
    return results, report
