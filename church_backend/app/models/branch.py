from app.extensions import db

class Branch(db.Model):
    __tablename__ = 'branches'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    timezone = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<branch {self.name}>"