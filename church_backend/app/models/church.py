from app import db

class church(db.Model):
    __tablename__ = 'church'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<church {self.name}>"