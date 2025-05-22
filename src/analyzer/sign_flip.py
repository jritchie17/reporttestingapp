import re
from typing import Iterable, Any


def _normalize_account(account: Any) -> str:
    """Return digits-only account identifier."""
    acct_str = str(account).strip()
    if not acct_str:
        return ""
    digits = re.findall(r"\d", acct_str)
    return "".join(digits)


def should_flip(account: Any, sign_flip_accounts: Iterable[str]) -> bool:
    """Return True if the value should have its sign flipped."""
    accounts = {_normalize_account(a) for a in sign_flip_accounts or []}
    return _normalize_account(account) in accounts


def apply(value: Any, account: Any, sign_flip_accounts: Iterable[str]):
    """Flip numeric value if the account is configured for flipping."""
    if not should_flip(account, sign_flip_accounts):
        return value
    try:
        return -float(value)
    except Exception:
        return value
