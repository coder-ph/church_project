from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.branch import Branch
from app.models.church import church
from flask_bcrypt import Bcrypt
from faker import Faker
from datetime import datetime
import uuid

faker = Faker()

app = create_app()
bcrypt = Bcrypt(app)

def reset_database():
    
    tables = [
        'likes',
        'comments',
        'conversation_threads',
        'event_contributions',
        'transactions',
        'event_branch_assignments',
        'events',
        'users',
        'branches',
        'church'
    ]
    
    
    with db.engine.connect() as connection:
        for table in tables:
            try:
                connection.execute(f'DROP TABLE IF EXISTS {table} CASCADE')
            except:
                pass  
    
    
    db.create_all()

with app.app_context():
   
    reset_database()

    
    ch = church(name="Global Church", description="Main church organization")
    db.session.add(ch)
    db.session.commit()

    
    branch = Branch(
        name="Nairobi Branch", 
        location="Nairobi",
        timezone="Africa/Nairobi"
    )
    db.session.add(branch)
    db.session.commit()

    
    superadmin = User(
        email="admin@church.org",
        full_name=faker.name(),
        username="superadmin",
        password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
        role="Superadmin",
        birth_year=datetime.strptime("1990-01-01", "%Y-%m-%d"),
        region="Global",
        phone_number="0740786838",
        branch_id=branch.id
    )

    admin = User(
        email="branchadmin@church.org",
        username="admin1",
        full_name=faker.name(),
        password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
        role="Admin",
        region="Nairobi",
        birth_year=datetime.strptime("1985-05-10", "%Y-%m-%d"),
        phone_number="0740786898",
        branch_id=branch.id
    )

    member = User(
        email="member@church.org",
        username="member1",
        full_name=faker.name(),
        password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
        role="Member",
        birth_year=datetime.strptime("2000-02-12", "%Y-%m-%d"),
        phone_number="0740786338",
        region="Nairobi",
        branch_id=branch.id
    )

    db.session.add_all([superadmin, admin, member])
    db.session.commit()

    print("✅ Seed data inserted successfully.")