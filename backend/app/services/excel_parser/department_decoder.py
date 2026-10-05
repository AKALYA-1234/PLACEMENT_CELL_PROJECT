"""
Utility to decode department name from a register number.
Register number format: 7376XXYYY where XX = dept code, YYY = student sequence.
Example: 7376231CD107 → dept code = CD → Computer Science and Design
"""

DEPT_CODE_MAP = {
    "CS": "Computer Science and Engineering",
    "CD": "Computer Science and Design",
    "CY": "Computer Science and Cyber Security",
    "CB": "Computer Science and Business Systems",
    "CA": "Computer Science and Engineering (AI&ML)",
    "CE": "Civil Engineering",
    "EC": "Electronics and Communication Engineering",
    "EE": "Electrical and Electronics Engineering",
    "ME": "Mechanical Engineering",
    "IT": "Information Technology",
    "AU": "Automobile Engineering",
    "BT": "Biotechnology",
    "CH": "Chemical Engineering",
    "RA": "Robotics and Automation",
    "FT": "Food Technology",
    "MC": "MCA",
    "MB": "MBA",
    "AI": "Artificial Intelligence and Machine Learning",
    "DS": "Data Science",
    "AD": "AIDS",
}

import re

REGISTER_PATTERN = re.compile(r"^7376\d{2}([A-Za-z]{2,3})\d+$", re.IGNORECASE)


def decode_department_from_register(register_number: str) -> str | None:
    """
    Attempt to extract dept from register number.
    Returns full department name or None if not decodable.
    """
    if not register_number:
        return None
    match = REGISTER_PATTERN.match(register_number.strip())
    if not match:
        return None
    dept_code = match.group(1).upper()
    return DEPT_CODE_MAP.get(dept_code, None)
