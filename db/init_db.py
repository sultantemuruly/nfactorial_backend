from db.database import Base, engine
from db.models import Users, Tasks

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
