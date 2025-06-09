from db.database import Base, engine
from db.models import Users, Tasks

Base.metadata.create_all(bind=engine)
