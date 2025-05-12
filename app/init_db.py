
from app.db import Base, engine
from app.models import product, category  # import the whole module

def init_db():
    Base.metadata.create_all(bind=engine)
