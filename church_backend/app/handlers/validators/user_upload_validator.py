# utils/validators.py

import re
import pandas as pd

REQUIRED_FIELDS = ["name", "email", "phone", "role"]

def validate_user_row(row):
    errors = []

    for field in REQUIRED_FIELDS:
        if pd.isnull(row.get(field)) or str(row.get(field)).strip() == "":
            errors.append(f"'{field}' is required.")

    email = str(row.get("email", "")).strip()
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors.append("Invalid email format.")

    phone = str(row.get("phone", "")).strip()
    if phone and not re.match(r"^\+?\d{7,15}$", phone):
        errors.append("Invalid phone number.")

    role = str(row.get("role", "")).strip().lower()
    allowed_roles = ["member", "leader", "admin"]  
    if role and role not in allowed_roles:
        errors.append(f"Invalid role. Must be one of: {', '.join(allowed_roles)}")

    return errors
