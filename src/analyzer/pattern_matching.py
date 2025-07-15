import pandas as pd
import numpy as np


def _cosine_similarity_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Return pairwise cosine similarity between two 2D arrays."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.ndim == 1:
        a = a.reshape(1, -1)
    if b.ndim == 1:
        b = b.reshape(1, -1)
    a_norm = np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = np.linalg.norm(b, axis=1, keepdims=True)
    a_norm[a_norm == 0] = 1e-12
    b_norm[b_norm == 0] = 1e-12
    return (a @ b.T) / (a_norm * b_norm.T)


def get_numeric_signature(row) -> np.ndarray:
    """Convert a row to a numeric signature array."""
    values = np.array(row, dtype=np.float64)
    return np.nan_to_num(values)


def match_rows_by_pattern(excel_df: pd.DataFrame, sql_df: pd.DataFrame, base_label: str):
    """Match ambiguous Excel rows to SQL rows by comparing numeric patterns."""
    excel_rows = excel_df[excel_df['Label'] == base_label].drop(columns='Label')
    sql_variants = sql_df[sql_df['Label'].str.startswith(base_label)].copy()

    excel_sigs = np.array([get_numeric_signature(row) for _, row in excel_rows.iterrows()])
    sql_sigs = np.array([get_numeric_signature(row.drop('Label')) for _, row in sql_variants.iterrows()])

    if excel_sigs.size == 0 or sql_sigs.size == 0:
        return {}

    similarities = _cosine_similarity_matrix(excel_sigs, sql_sigs)

    match_map = {}
    used_sql = set()
    for i, sim_row in enumerate(similarities):
        best_idx = int(np.argmax(sim_row))
        while best_idx in used_sql:
            sim_row[best_idx] = -1
            best_idx = int(np.argmax(sim_row))
        used_sql.add(best_idx)
        match_map[i] = sql_variants.iloc[best_idx]['Label']

    return match_map
