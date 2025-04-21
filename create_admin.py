from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.drop_all()  # Optional: resets all tables if you're early in dev
    db.create_all()
    
    user = User(
        username="admin",
        password=generate_password_hash("admin"),
        role="admin"
    )
    db.session.add(user)
    db.session.commit()

    print("✅ Admin user created successfully.")
