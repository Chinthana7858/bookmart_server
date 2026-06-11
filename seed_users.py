from app.auth.utils import hash_password
from app.db import SessionLocal
from app.models.user import User


USERS = [
    {
        "name": "Admin",
        "email": "admin@bookmart.local",
        "password": "admin123",
        "address": "BookMart Admin Office",
        "role": "admin",
    },
    {
        "name": "Test User",
        "email": "user@bookmart.local",
        "password": "user123",
        "address": "123 Reader Street",
        "role": "user",
    },
]


def seed_users():
    db = SessionLocal()
    try:
        for user_data in USERS:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                print(f"Skipping existing user: {user_data['email']}")
                continue

            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password=hash_password(user_data["password"]),
                address=user_data["address"],
                role=user_data["role"],
            )
            db.add(user)
            print(f"Added user: {user_data['email']}")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
