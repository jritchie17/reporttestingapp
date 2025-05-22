"""Regular expressions for extracting account numbers from text."""

# Accounts are expected to be in the format ``XXXX-XXXX`` where the prefix may
# optionally start with a single letter.  Examples include ``6101-6001`` and
# ``R101-0000``.  Previous patterns attempted to match many other digit
# combinations which resulted in unrelated numeric values being captured when
# scanning spreadsheets.  The patterns below focus only on the supported
# account formats.

ACCOUNT_PATTERNS = [
    # Letter prefix followed by three digits and a four digit suffix
    r"([A-Za-z]\d{3}-\d{4})",
    # Four digit prefix followed by four digit suffix
    r"(\d{4}-\d{4})",
]
