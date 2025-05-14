from fastapi import FastAPI
from app.routers import product, category
from app.routers.user import router as user_router 
from app.auth.router import router as auth_router
from app.routers.user_activity import router as user_activity_router
from app.routers.co_engagement_status import router as co_engagement_router
from app.routers.recommendation import router as recommendation
from app.routers.cart_item import router as cart_item
from app.routers.order import router as order
from app.init_db import init_db
from app.services.scheduler import start_scheduler
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mybookmarket.netlify.app"],  
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
start_scheduler()




# uvicorn app.main:app --reload
