from db.database import Base, engine
from db.models import Users, Books

Base.metadata.create_all(bind=engine)
