from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.product import Product
from app.models.recommendation import Recommendation
from app.models.co_engagement_stats import CoEngagementStats

def generate_recommendations(db: Session):
    print("recommendations-----------")

    db.query(Recommendation).delete()
    db.commit()

    co_engagements = db.query(CoEngagementStats).all()

    for row in co_engagements:
        a = row.product_id_a
        b = row.product_id_b

        if a == b:
            continue

        score = (
            1 * (row.co_view_count or 0) +
            3 * (row.co_add_cart_count or 0) +
            5 * (row.co_buy_count or 0)
        )

        now = datetime.utcnow()

        db.add(Recommendation(
            base_product_id=a,
            recommended_product_id=b,
            score=score,
            created_at=now
        ))

        db.add(Recommendation(
            base_product_id=b,
            recommended_product_id=a,
            score=score,
            created_at=now
        ))


    db.commit()


def get_recommendations(base_product_id: int, db: Session) -> list[Product]:
    # Get top recommendations
    recs = (
        db.query(Recommendation.recommended_product_id)
        .filter(Recommendation.base_product_id == base_product_id)
        .order_by(Recommendation.score.desc())
        .limit(5)
        .all()
    )
    recommended_ids = [r[0] for r in recs]

    # if fewer than 5
    if len(recommended_ids) < 5:
        needed = 5 - len(recommended_ids)
        fallback = (
            db.query(Product.id)
            .filter(~Product.id.in_(recommended_ids + [base_product_id]))
            .order_by(func.random())
            .limit(needed)
            .all()
        )
        fallback_ids = [f[0] for f in fallback]
        recommended_ids.extend(fallback_ids)

    #Fetch final products
    products = db.query(Product).filter(Product.id.in_(recommended_ids)).all()
    return products