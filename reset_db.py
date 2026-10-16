from app.database import SessionLocal
from app.models import NewsItem

db = SessionLocal()
count = db.query(NewsItem).update({NewsItem.is_notified: False})
db.commit()
db.close()
print(f"Reset is_notified=False for {count} news items.")
