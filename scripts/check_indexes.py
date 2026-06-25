from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/school_management")

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    try:
        res = conn.execute(text("SHOW INDEX FROM students"))
        for row in res.fetchall():
            print(f"Table: {row[0]}, Non_unique: {row[1]}, Key_name: {row[2]}, Seq_in_index: {row[3]}, Column_name: {row[4]}")
    except Exception as e:
        print(f"Error checking indexes: {e}")
