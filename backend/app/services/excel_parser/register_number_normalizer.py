import re
from typing import Any

# Standard college register number format (e.g. 7376231CS333, 7376232AD101, 7376242AD501)
REGISTER_REGEX = re.compile(r"^7376\d{2}[A-Za-z0-9]{5,6}$", re.IGNORECASE)


def normalize_register_number(raw_val: Any) -> tuple[str | None, bool, str | None]:
    """
    Cleans and validates a register number.
    Returns:
        (normalized_str, is_valid, error_message)
    """
    if raw_val is None:
        return None, False, "Register number is empty"

    val_str = str(raw_val).strip()

    # Handle float formatting e.g. 7.376231e+11 or 737623100.0
    if isinstance(raw_val, float):
        if val_str.endswith(".0"):
            val_str = val_str[:-2]
        elif "e" in val_str.lower():
            try:
                val_str = f"{int(raw_val)}"
            except Exception:
                pass

    # Remove any internal whitespace or zero-width spaces
    cleaned = re.sub(r"\s+", "", val_str).upper()

    if not cleaned or cleaned in ("NONE", "NULL", "NAN", "-", ""):
        return None, False, "Register number is empty"

    # Validate length and format
    if REGISTER_REGEX.match(cleaned):
        return cleaned, True, None

    # Check common anomaly types
    if cleaned.isdigit() and len(cleaned) == 10 and not cleaned.startswith("7376"):
        return cleaned, False, f"Malformed register number: looks like a phone number ('{cleaned}')"

    if cleaned.startswith("7377"):
        return cleaned, False, f"Malformed register number: invalid batch prefix ('{cleaned}')"

    return cleaned, False, f"Invalid register number pattern ('{cleaned}')"
