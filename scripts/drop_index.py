from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/school_management")

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    try:
        # Dropping the legacy composite index on school_id / enroll_no
        conn.execute(text("ALTER TABLE students DROP INDEX school_id"))
        conn.commit()
        print("Successfully dropped legacy unique index 'school_id' (on enroll_no).")
    except Exception as e:
        print(f"Error dropping index: {e}")
