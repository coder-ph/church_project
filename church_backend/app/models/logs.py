from app import db
import datetime


class ApiLog(db.Model):
    __tablename__ = 'apilogs'
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(100))
    request_body = db.Column(db.JSON)
    response_body = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def log(endpoint, request_body, response_body):
        db.session.add(ApiLog(
            endpoint=endpoint,
            request_body=request_body,
            response_body=response_body
        ))
        db.session.commit()
