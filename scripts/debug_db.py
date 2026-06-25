from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/school_management")

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    try:
        res_schools = conn.execute(text("SELECT id FROM schools"))
        schools = [r[0] for r in res_schools.fetchall()]
        print(f"Available Schools: {schools}")
        
        res_classes = conn.execute(text("SELECT id, class_name FROM classes"))
        classes = [{"id": r[0], "name": r[1]} for r in res_classes.fetchall()]
        print(f"Available Classes: {classes}")
        
        res_students = conn.execute(text("SELECT admission_number FROM students"))
        students = [r[0] for r in res_students.fetchall()]
        print(f"Existing Admission Numbers (first 10): {students[:10]}")
    except Exception as e:
        print(f"Error checking DB: {e}")
