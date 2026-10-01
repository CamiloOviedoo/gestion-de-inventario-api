import os

from app.database import SessionLocal
from app.services.admin import create_initial_admin

def main():
    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    
    if not username or not email or not password:
        raise RuntimeError("ADMIN_USERNAME, ADMIN_EMAIL, and ADMIN_PASSWORD must be configured")
    
    db = SessionLocal()
    
    try:
        admin = create_initial_admin(
            db=db,
            username=username,
            email=email,
            password=password
        )
        
        print(f"Admin ready: {admin.username}")
    
    finally:
        db.close()
       
if __name__ == "__main__":
    main()        
            