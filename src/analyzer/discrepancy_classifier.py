import pandas as pd

"""Utility for classifying account discrepancies by severity."""


def classify(discrepancies_df: pd.DataFrame) -> pd.DataFrame:
    """Assign severity levels to discrepancies.

    Parameters
    ----------
    discrepancies_df : pd.DataFrame
        Output of ``ComparisonEngine.identify_account_discrepancies`` before
        classification.

    Returns
    -------
    pd.DataFrame
        The same dataframe with a new ``Severity`` column containing
        labels such as ``"minor"`` or ``"major"``.
    """
    if discrepancies_df is None or discrepancies_df.empty:
        return discrepancies_df.assign(Severity=[])

    df = discrepancies_df.copy()
    df["Severity"] = "minor"

    if "Variance" in df.columns:
        abs_var = df["Variance"].abs().fillna(0)
        if abs_var.count() <= 1:
            threshold = 0
        else:
            threshold = abs_var.median() + abs_var.std()
            if pd.isna(threshold):
                threshold = abs_var.median()
        df.loc[abs_var > threshold, "Severity"] = "major"

    if set(["Missing in Excel", "Missing in SQL"]).issubset(df.columns):
        df.loc[df["Missing in Excel"] | df["Missing in SQL"], "Severity"] = "major"

    return df
