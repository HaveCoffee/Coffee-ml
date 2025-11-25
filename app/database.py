from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "postgresql://coffee_user:coffee_pass@localhost/coffee_db"
# SQLALCHEMY_DATABASE_URL = "postgresql://coffee_user:coffee_pass@localhost/coffee_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()