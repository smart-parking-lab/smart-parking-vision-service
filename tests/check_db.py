import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def check_db_schema():
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    tables = ["parking_sessions", "vehicles", "parking_slots", "invoices"]
    
    print("--- KIỂM TRA CẤU TRÚC DATABASE ---")
    for table in tables:
        print(f"\nBảng: {table}")
        columns = inspector.get_columns(table)
        for col in columns:
            print(f" - {col['name']} ({col['type']})")

if __name__ == "__main__":
    check_db_schema()
