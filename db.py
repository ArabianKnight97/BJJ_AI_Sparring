from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual connection string
DATABASE_URL = "postgresql://postgres:Spyro97!@localhost:5432/bjj_game"

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
