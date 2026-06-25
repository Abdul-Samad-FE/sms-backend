from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/school_management")

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    try:
        # 1. Modify enroll_no to be NULLABLE so it doesn't default to "" (which causes duplicates)
        print("Making enroll_no nullable...")
        conn.execute(text("ALTER TABLE students MODIFY COLUMN enroll_no VARCHAR(50) NULL"))
        
        # 2. Add a standard index for school_id (to keep the Foreign Key happy)
        print("Adding non-unique index for school_id...")
        conn.execute(text("CREATE INDEX idx_school_id ON students (school_id)"))
        
        # 3. Drop the legacy composite unique index that's causing conflicts
        print("Dropping legacy composite unique index...")
        conn.execute(text("ALTER TABLE students DROP INDEX school_id"))
        
        conn.commit()
        print("Successfully updated physical database constraints.")
    except Exception as e:
        print(f"Error fixing constraints: {e}")
