from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.product import Product
from app.schemas.product import ProductOut
from app.services.recommendation_service import generate_recommendations, get_recommendations
from app.models.recommendation import Recommendation
from app.schemas.recommendation import RecommendationOut

router = APIRouter()

@router.post("/generate")
def generate(db: Session = Depends(get_db)):
    generate_recommendations(db)
    return {"message": "Recommendations generated"}

@router.get("/recommendations", response_model=list[RecommendationOut])
def get_all_recommendations(db: Session = Depends(get_db)):
    return db.query(Recommendation).all()


@router.get("/recommendations/{base_product_id}", response_model=list[ProductOut])
def fetch_recommendations(base_product_id: int, db: Session = Depends(get_db)):
    products = get_recommendations(base_product_id, db)
    if not products:
        raise HTTPException(status_code=404, detail="No recommendations found.")
    return products