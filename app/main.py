from fastapi import FastAPI
from app.routers import product, category
from app.routers.user import router as user_router 
from app.auth.router import router as auth_router
from app.routers.user_activity import router as user_activity_router
from app.routers.co_engagement_status import router as co_engagement_router
from app.routers.recommendation import router as recommendation
from app.routers.cart_item import router as cart_item
from app.routers.order import router as order
from app.routers.payment import router as payment
from app.routers.admin_user import router as admin_user
from app.routers.admin_dashboard import router as admin_dashboard
from app.init_db import init_db
from app.services.scheduler import start_scheduler
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

DEFAULT_CORS_ORIGINS = [
    "https://mybookmarket.netlify.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", ",".join(DEFAULT_CORS_ORIGINS)).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
app.include_router(product.router, prefix="/products", tags=["Products"])
app.include_router(category.router, prefix="/categories", tags=["Categories"])
app.include_router(user_router) 
app.include_router(auth_router) 
app.include_router(user_activity_router) 
app.include_router(co_engagement_router) 
app.include_router(recommendation) 
app.include_router(cart_item) 
app.include_router(order) 
app.include_router(payment)
app.include_router(admin_user)
app.include_router(admin_dashboard)
start_scheduler()




# uvicorn app.main:app --reload
