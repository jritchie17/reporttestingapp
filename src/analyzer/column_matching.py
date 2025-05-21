import re
from difflib import SequenceMatcher
from typing import Iterable, List, Dict


def normalize_column_names(columns: Iterable[str]) -> List[str]:
    """Normalize column names for fuzzy matching."""
    normalized = []
    for col in columns:
        if not isinstance(col, str):
            col = str(col)
        col = re.sub(r"[^\w\s]", " ", col)
        col = re.sub(r"\b(the|and|or|of|in|for|to|a|an)\b", "", col, flags=re.IGNORECASE)
        col = re.sub(r"\s+", " ", col).strip().lower()
        normalized.append(col)
    return normalized


def find_matching_columns(excel_columns: Iterable[str], sql_columns: Iterable[str], threshold: float = 0.6) -> Dict[int, Dict[str, object]]:
    """Return mappings of Excel column index to SQL column info."""
    excel_normalized = normalize_column_names(excel_columns)
    sql_normalized = normalize_column_names(sql_columns)

    mappings: Dict[int, Dict[str, object]] = {}
    used_sql = set()

    # exact matches
    for i, e in enumerate(excel_normalized):
        for j, s in enumerate(sql_normalized):
            if j in used_sql:
                continue
            if e == s:
                mappings[i] = {"excel_column": list(excel_columns)[i], "sql_column": list(sql_columns)[j], "match_score": 1.0}
                used_sql.add(j)
                break

    # fuzzy matches
    for i, e in enumerate(excel_normalized):
        if i in mappings:
            continue
        best = None
        best_score = threshold
        for j, s in enumerate(sql_normalized):
            if j in used_sql:
                continue
            score1 = SequenceMatcher(None, e, s).ratio()
            e_words = set(e.split())
            s_words = set(s.split())
            score2 = len(e_words & s_words) / max(len(e_words), len(s_words)) if (e_words or s_words) else 0
            score3 = 0
            if e in s or s in e:
                min_len = min(len(e), len(s))
                max_len = max(len(e), len(s))
                score3 = min_len / max_len if max_len > 0 else 0
            score = max(score1, score2, score3)
            if score > best_score:
                best_score = score
                best = j
        if best is not None:
            mappings[i] = {"excel_column": list(excel_columns)[i], "sql_column": list(sql_columns)[best], "match_score": best_score}
            used_sql.add(best)
    return mappings
