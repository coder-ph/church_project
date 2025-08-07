
import pandas as pd
from io import BytesIO
from models.user import User
from models.logs import ApiLog
from validators import validate_user_row
from app import db
from models.user import User

def get_branch_id_for_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"User with ID {user_id} does not exist.")
    return user.branch_id

def process_user_upload(file, uploader_id):
    df = pd.read_excel(BytesIO(file.read()))
    successes, failures = [], []

    for idx, row in df.iterrows():
        errors = validate_user_row(row)

        if errors:
            failures.append({"row": idx + 2, "errors": errors})
            continue

        try:
            user = User(
                name=row["name"],
                email=row["email"],
                phone=row["phone"],
                role=row["role"],
                branch_id=get_branch_id_for_user(uploader_id)
            )
            db.session.add(user)
            db.session.flush()
            successes.append({"row": idx + 2, "id": user.id})
        except Exception as e:
            db.session.rollback()
            failures.append({"row": idx + 2, "errors": [str(e)]})

    db.session.commit()

    log = ApiLog(
        action="bulk_user_upload",
        user_id=uploader_id,
        details={"successes": len(successes), "failures": len(failures)}
    )
    db.session.add(log)
    db.session.commit()

    return {"successes": successes, "failures": failures}
