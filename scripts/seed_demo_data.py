"""Seed demo data for a multi-tenant walkthrough.

Creates two schools, each with grade levels Play Group -> Class 5, 11-20
random students per class, 5 teachers, and one school admin. Idempotent at
the school level: a school that already exists (by emis_code) is skipped.

Run from the sms-backend directory:
    venv\\Scripts\\python.exe -m scripts.seed_demo_data
"""

import random
from datetime import datetime, timedelta

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.class_model import Class
from app.models.role import Role
from app.models.school import School
from app.models.student import Student
from app.models.user import User

CLASS_NAMES = ["Play Group", "Class 1", "Class 2", "Class 3", "Class 4"]

SCHOOLS = [
    {
        "emis_code": "DEMO-A",
        "name": "Green Valley High School",
        "uc_name": "UC-5 Central",
        "address": "12 Garden Road, Greenfield",
        "slug": "greenvalley",
        "admin_password": "GreenAdmin@123",
        "teacher_password": "Teacher@123",
    },
    {
        "emis_code": "DEMO-B",
        "name": "Sunrise Public School",
        "uc_name": "UC-9 North",
        "address": "44 Sunrise Avenue, Easttown",
        "slug": "sunrise",
        "admin_password": "SunriseAdmin@123",
        "teacher_password": "Teacher@123",
    },
]

FIRST_NAMES = [
    "Ali", "Sara", "Bilal", "Ayesha", "Hamza", "Fatima", "Usman", "Zainab",
    "Ahmed", "Hira", "Saad", "Maryam", "Hassan", "Noor", "Umar", "Iqra",
    "Talha", "Amna", "Faizan", "Komal", "Danish", "Mahnoor", "Rehan", "Sana",
]
LAST_NAMES = [
    "Khan", "Malik", "Sheikh", "Butt", "Chaudhry", "Raza", "Hussain", "Iqbal",
    "Javed", "Farooq", "Aslam", "Nawaz", "Bhatti", "Qureshi", "Siddiqui",
]
GENDERS = ["Male", "Female"]


def rand_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def rand_phone():
    return "03" + "".join(random.choice("0123456789") for _ in range(9))


def rand_dob(min_age, max_age):
    age_days = random.randint(min_age * 365, max_age * 365)
    return datetime.now() - timedelta(days=age_days)


def seed_school(db, role_teacher_id, role_admin_id, info):
    existing = db.query(School).filter(School.emis_code == info["emis_code"]).first()
    if existing is not None:
        print(f"  - School '{info['name']}' already exists (id={existing.id}); skipping.")
        return existing, 0, 0, 0

    school = School(
        emis_code=info["emis_code"],
        name=info["name"],
        uc_name=info["uc_name"],
        address=info["address"],
    )
    db.add(school)
    db.commit()
    db.refresh(school)

    # Classes
    classes = []
    for name in CLASS_NAMES:
        cls = Class(school_id=school.id, class_name=name, section="A")
        db.add(cls)
        classes.append(cls)
    db.commit()
    for cls in classes:
        db.refresh(cls)

    # Students per class (11-20)
    student_count = 0
    seq = 1
    for idx, cls in enumerate(classes):
        n = random.randint(11, 20)
        # Younger grades -> younger students
        min_age = 3 + idx
        max_age = 5 + idx
        for _ in range(n):
            admission_number = f"{info['emis_code']}-{seq:04d}"
            seq += 1
            student = Student(
                school_id=school.id,
                name=rand_name(),
                admission_number=admission_number,
                father_name=rand_name(),
                father_contact=rand_phone(),
                address=info["address"],
                status="Active",
                class_id=cls.id,
                section="A",
                gender=random.choice(GENDERS),
                dob=rand_dob(min_age, max_age),
                admission_date=datetime.now() - timedelta(days=random.randint(30, 1000)),
            )
            db.add(student)
            student_count += 1
    db.commit()

    # 5 teachers
    for t in range(1, 6):
        email = f"teacher{t}.{info['slug']}@sms.com"
        if db.query(User).filter(User.email == email).first():
            continue
        db.add(
            User(
                school_id=school.id,
                role_id=role_teacher_id,
                name=f"{rand_name()} (Teacher)",
                email=email,
                password=hash_password(info["teacher_password"]),
                is_active=True,
                is_superuser=False,
                is_first_login=True,
            )
        )

    # 1 school admin
    admin_email = f"admin.{info['slug']}@sms.com"
    if not db.query(User).filter(User.email == admin_email).first():
        db.add(
            User(
                school_id=school.id,
                role_id=role_admin_id,
                name=f"{info['name']} Admin",
                email=admin_email,
                password=hash_password(info["admin_password"]),
                is_active=True,
                is_superuser=False,
                is_first_login=True,
            )
        )
    db.commit()

    print(
        f"  + School '{info['name']}' (id={school.id}): "
        f"{len(classes)} classes, {student_count} students, 5 teachers, 1 admin."
    )
    print(f"      admin login: {admin_email} / {info['admin_password']}")
    return school, len(classes), student_count, 5


def main():
    random.seed(42)  # reproducible demo data
    db = SessionLocal()
    try:
        role_teacher = db.query(Role).filter(Role.role_name == "teacher").first()
        role_admin = db.query(Role).filter(Role.role_name == "admin").first()
        if role_teacher is None or role_admin is None:
            raise SystemExit(
                "Roles not seeded. Start the app once so seeds run, then retry."
            )

        print("Seeding demo data...")
        for info in SCHOOLS:
            seed_school(db, role_teacher.id, role_admin.id, info)
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
