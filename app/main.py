import logging
import sys
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.database import init_db, SessionLocal
from app.models import NewsItem, SourceType
from app.ingest import BlogIngester, YouTubeIngester
from app.llm import SummarizationAgent
from app.notify import EmailNotifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("ai_news_aggregator")


def run_pipeline():
    """Main execution pipeline."""
    logger.info("=== Starting AI News Aggregator Pipeline ===")
    
    # 1. Initialize Database Schema
    logger.info("Initializing Database...")
    init_db()
    db: Session = SessionLocal()

    try:
        # 2. Ingest Latest News Items
        logger.info("--- Step 1: Ingesting Feed Data ---")
        
        # Blog feeds
        blog_ingester = BlogIngester(
            feed_urls=settings.blog_feed_list,
            max_items=settings.DEFAULT_MAX_ITEMS_PER_FEED
        )
        blog_items = blog_ingester.fetch_all()
        logger.info(f"Ingested {len(blog_items)} blog posts.")

        # YouTube feeds
        youtube_ingester = YouTubeIngester(
            channel_ids=settings.youtube_channel_list,
            max_items=settings.DEFAULT_MAX_ITEMS_PER_FEED
        )
        youtube_items = youtube_ingester.fetch_all()
        logger.info(f"Ingested {len(youtube_items)} YouTube videos.")

        all_fetched_items = blog_items + youtube_items
        new_inserted_count = 0

        # Save to database (deduplicate by URL)
        for item_data in all_fetched_items:
            existing = db.query(NewsItem).filter(NewsItem.url == item_data["url"]).first()
            if not existing:
                news_item = NewsItem(
                    title=item_data["title"],
                    url=item_data["url"],
                    source_type=item_data["source_type"],
                    source_name=item_data["source_name"],
                    published_at=item_data["published_at"],
                    raw_content=item_data["raw_content"],
                    is_summarized=False,
                    is_notified=False,
                )
                db.add(news_item)
                new_inserted_count += 1

        db.commit()
        logger.info(f"Successfully inserted {new_inserted_count} new news items into DB.")

        # 3. LLM Summarization
        logger.info("--- Step 2: Summarizing Pending Items ---")
        pending_items = db.query(NewsItem).filter(NewsItem.is_summarized == False).all()
        logger.info(f"Found {len(pending_items)} items pending LLM summarization.")

        agent = SummarizationAgent()
        import time
        for idx, item in enumerate(pending_items):
            logger.info(f"Summarizing item #{item.id}: {item.title}")
            res = agent.summarize(
                title=item.title,
                source_name=item.source_name,
                source_type=item.source_type,
                raw_content=item.raw_content or "",
            )
            item.ai_summary = res["summary"]
            item.category = res["category"]
            item.is_summarized = True
            db.commit()
            if idx < len(pending_items) - 1:
                time.sleep(12)  # Respect Gemini Free-Tier 5 RPM rate limit

        # 4. Dispatch Email Digest
        logger.info("--- Step 3: Dispatching Email Notifications ---")
        items_to_notify = db.query(NewsItem).filter(
            NewsItem.is_summarized == True,
            NewsItem.is_notified == False
        ).all()

        if items_to_notify:
            logger.info(f"Preparing notification digest for {len(items_to_notify)} items.")
            notifier = EmailNotifier()
            sent_success = notifier.send_digest(items_to_notify)

            if sent_success:
                for item in items_to_notify:
                    item.is_notified = True
                db.commit()
                logger.info(f"Marked {len(items_to_notify)} items as notified.")
            else:
                logger.warning("Email dispatch did not send (check credentials or SMTP config).")
        else:
            logger.info("No un-notified summarized items available.")

        logger.info("=== AI News Aggregator Pipeline Completed Successfully ===")

    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    run_pipeline()
