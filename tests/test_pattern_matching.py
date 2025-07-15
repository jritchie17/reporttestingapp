import pandas as pd
from src.analyzer.pattern_matching import match_rows_by_pattern


def test_match_rows_by_pattern_basic():
    excel_df = pd.DataFrame({
        'Label': ['6101 GI Revenue'] * 3,
        'Jan': [1000, 0.5, 100],
        'Feb': [2000, 0.6, 200],
    })
    sql_df = pd.DataFrame({
        'Label': [
            '6101 GI Revenue',
            '6101 GI Revenue percentage',
            '6101 GI Revenue per procedure',
        ],
        'Jan': [1000, 0.5, 100],
        'Feb': [2000, 0.6, 200],
    })

    mapping = match_rows_by_pattern(excel_df, sql_df, '6101 GI Revenue')
    assert mapping == {
        0: '6101 GI Revenue',
        1: '6101 GI Revenue percentage',
        2: '6101 GI Revenue per procedure',
    }
