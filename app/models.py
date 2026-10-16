from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
import enum
from app.database import Base


class SourceType(str, enum.Enum):
    BLOG = "blog"
    YOUTUBE = "youtube"


class NewsItem(Base):
    """Database model for aggregated news items."""

    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(512), nullable=False)
    url = Column(String(1024), unique=True, index=True, nullable=False)
    source_type = Column(String(50), nullable=False, default=SourceType.BLOG.value)
    source_name = Column(String(255), nullable=False)
    published_at = Column(DateTime, nullable=True)
    raw_content = Column(Text, nullable=True)
    
    # LLM Summarization fields
    ai_summary = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Workflow status flags
    is_summarized = Column(Boolean, default=False, nullable=False, index=True)
    is_notified = Column(Boolean, default=False, nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<NewsItem id={self.id} title='{self.title[:30]}...' source='{self.source_name}'>"
