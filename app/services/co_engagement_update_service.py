from sqlalchemy.orm import Session
from app.models.user_activity import UserActivity
from app.models.co_engagement_stats import CoEngagementStats
from sqlalchemy import and_, or_
from collections import defaultdict
from datetime import datetime
from app.models.category import Category

def update_co_engagement_stats(db: Session):
    print("Updating co-engagements--------------------")

    # Clear existing stats
    db.query(CoEngagementStats).delete()
    db.commit()

    sessions = db.query(UserActivity.session_id).distinct().all()
    if not sessions:
        print("No sessions")
        return

    engagement_map = defaultdict(lambda: {"co_view_count": 0, "co_add_cart_count": 0, "co_buy_count": 0})

    for (session_id,) in sessions:
        actions = db.query(UserActivity).filter_by(session_id=session_id).all()
        action_groups = defaultdict(list)

        for action in actions:
            action_groups[action.action].append(action.product_id)
            print(action.action)
        for action_type, product_ids in action_groups.items():
            for i in range(len(product_ids)):
                for j in range(i + 1, len(product_ids)):
                    a, b = sorted((product_ids[i], product_ids[j]))
                    if a == b:
                        continue
                    key = (a, b)
                    if action_type == "view":
                        engagement_map[key]["co_view_count"] += 1
                    elif action_type == "add_to_cart":
                        engagement_map[key]["co_add_cart_count"] += 1
                    elif action_type == "buy":
                        engagement_map[key]["co_buy_count"] += 1

    # Bulk insert
    for (a, b), stats in engagement_map.items():
        db.add(CoEngagementStats(
            product_id_a=a,
            product_id_b=b,
            co_view_count=stats["co_view_count"],
            co_add_cart_count=stats["co_add_cart_count"],
            co_buy_count=stats["co_buy_count"],
            last_updated=datetime.utcnow()
        ))

    db.commit()
    print("Co-engagement stats updated ---------------------")




def get_all_co_engagement_stats(db: Session):
    return db.query(CoEngagementStats).all()