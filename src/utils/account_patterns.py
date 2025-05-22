"""Common regular expressions for locating account identifiers in text."""

# Accounts in the application always follow the ``XXXX-XXXX`` convention
# where ``X`` may be a digit or a letter (e.g. ``6101-6001`` or ``R101-0000``).
# Keeping this single pattern avoids matching unrelated numeric values such as
# dollar amounts.

ACCOUNT_PATTERNS = [r"([A-Za-z0-9]{4}-[A-Za-z0-9]{4})"]

