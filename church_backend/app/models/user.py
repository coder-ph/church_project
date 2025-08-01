from app import db
from flask_bcrypt import generate_password_hash, check_password_hash
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone_number = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default='member')
    username = db.Column(db.String, nullable=False)
    region = db.Column(db.String, nullable=False)
    birth_year = db.Column(db.DateTime, nullable=False)

    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    branch = db.relationship("Branch", backref=db.backref("users", lazy=True))

    def set_password(self, password):

        self.password_hash=generate_password_hash(password).decode('utf8')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.full_name}>"
