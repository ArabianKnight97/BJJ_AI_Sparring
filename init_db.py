from db import Base, engine

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
