"""Remove demo + legacy schools so the demo can be re-seeded from scratch.

Deletes the schools listed below by emis_code; SQLAlchemy cascades remove their
classes, students, attendance, and school-bound users. The cross-tenant
superadmin (school_id = NULL) is untouched.

Run from the sms-backend directory:
    venv\\Scripts\\python.exe -m scripts.reset_demo_data
"""

from app.db.session import SessionLocal
from app.models.school import School

# Legacy near-empty school + the two demo tenants.
EMIS_TO_DELETE = ["SMS-001", "DEMO-A", "DEMO-B"]


def main():
    db = SessionLocal()
    try:
        for emis in EMIS_TO_DELETE:
            school = db.query(School).filter(School.emis_code == emis).first()
            if school is None:
                print(f"  - {emis}: not found; skipping.")
                continue
            name = school.name
            db.delete(school)  # ORM cascade removes children
            db.commit()
            print(f"  x Deleted school '{name}' ({emis}) and all its data.")
        print("Reset complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
