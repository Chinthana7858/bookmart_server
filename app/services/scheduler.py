from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.services.co_engagement_update_service import update_co_engagement_stats
from app.services.recommendation_service import generate_recommendations


def run_coengagement_job():
    db: Session = SessionLocal()
    try:
        update_co_engagement_stats(db)
        generate_recommendations(db)
        print(" Co-engagement stats updated.")
    except Exception as e:
        print("Error in co-engagement job:", e)
    finally:
        db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_coengagement_job, 'interval', minutes=100) 
    scheduler.start()
