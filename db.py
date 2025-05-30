from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual connection string
DATABASE_URL = "**"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, index=True)
    fighter1 = Column(JSON)
    fighter2 = Column(JSON)
    log = Column(JSON)
    turn = Column(Integer)
    round = Column(Integer)
    belt_level = Column(String)

print("Connecting to:", DATABASE_URL)
