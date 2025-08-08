

from app.extensions import db
import uuid
from sqlalchemy.dialects.postgresql import JSON

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    action = db.Column(db.String, nullable=False)
    details = db.Column(JSON)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
