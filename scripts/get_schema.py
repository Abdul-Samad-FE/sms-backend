from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/school_management")

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    try:
        res = conn.execute(text("SHOW CREATE TABLE students"))
        print(res.fetchone()[1])
    except Exception as e:
        print(f"Error checking table creation: {e}")
