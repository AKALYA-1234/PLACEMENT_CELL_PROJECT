from typing import Any


def normalize_candidate_status(raw_val: Any, default_status: str = "QUALIFIED") -> str:
    """
    Normalizes status string to one of: QUALIFIED, DISQUALIFIED, ABSENT, OFFERED, ACCEPTED.
    """
    if raw_val is None:
        return default_status

    cleaned = str(raw_val).strip().upper()

    if not cleaned or cleaned in ("NONE", "NULL", "NAN", "-", ""):
        return default_status

    if any(term in cleaned for term in ["ABSENT", "AB", "NOT ATTENDED"]):
        return "ABSENT"

    if any(term in cleaned for term in ["REJECTED", "NOT SELECTED", "DISQUALIFIED", "FAIL"]):
        return "DISQUALIFIED"

    if any(term in cleaned for term in ["ACCEPTED", "JOINED"]):
        return "ACCEPTED"

    if any(term in cleaned for term in ["OFFERED", "PLACED", "OFFER"]):
        return "OFFERED"

    if any(term in cleaned for term in ["QUALIFIED", "SELECTED", "SHORTLISTED", "PASS", "PRESENT"]):
        return "QUALIFIED"

    return default_status
