
from app.db import Base, engine
from app.migrations import run_compat_migrations
from app.models import (
    cart_item,
    category,
    co_engagement_stats,
    order,
    product,
    recommendation,
    user,
    user_activity,
)

def init_db():
    Base.metadata.create_all(bind=engine)
    run_compat_migrations(engine)
