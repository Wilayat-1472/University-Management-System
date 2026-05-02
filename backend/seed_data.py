import logging
from app.database import SessionLocal, create_tables
from app.models.role import Role
from app.schemas.user import UserCreate
from app.services.user_service import create_user, get_user_by_username

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db) -> None:
    # Check if roles exist
    student_role = db.query(Role).filter(Role.name == "Student").first()
    if not student_role:
        db.add(Role(name="Student", description="Student access"))
        db.add(Role(name="Faculty", description="Faculty access"))
        db.add(Role(name="Admin", description="Full system access"))
        db.commit()
        logger.info("Roles created.")
        
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    
    # Check if admin exists
    user = get_user_by_username(db, username="admin")
    if not user:
        user_in = UserCreate(
            username="admin",
            email="admin@ums.edu",
            password="adminpassword",
            role_id=admin_role.id
        )
        user = create_user(db, user=user_in)
        logger.info(f"Admin user created: {user.username}")
    else:
        logger.info("Admin user already exists.")

def main() -> None:
    logger.info("Creating initial data")
    create_tables()
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    logger.info("Initial data created")

if __name__ == "__main__":
    main()
