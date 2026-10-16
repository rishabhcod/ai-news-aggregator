from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # Database
    DATABASE_URL: str = "sqlite:///./ai_news.db"  # Fallback to SQLite if MySQL not configured

    # Gemini LLM
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"

    # SMTP Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "AI News Digest <noreply@ainews.com>"
    EMAIL_TO: str = ""

    # Feed sources
    BLOG_FEEDS: str = (
        "https://openai.com/news/rss.xml,"
        "https://huggingface.co/blog/feed.xml,"
        "https://blog.google/technology/ai/rss/"
    )
    YOUTUBE_CHANNELS: str = "UCbfYPyITQ-shared"

    DEFAULT_MAX_ITEMS_PER_FEED: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def blog_feed_list(self) -> List[str]:
        """Returns parsed list of blog feed URLs."""
        if not self.BLOG_FEEDS:
            return []
        return [url.strip() for url in self.BLOG_FEEDS.split(",") if url.strip()]

    @property
    def youtube_channel_list(self) -> List[str]:
        """Returns parsed list of YouTube channel IDs."""
        if not self.YOUTUBE_CHANNELS:
            return []
        return [cid.strip() for cid in self.YOUTUBE_CHANNELS.split(",") if cid.strip()]

    @property
    def email_to_list(self) -> List[str]:
        """Returns parsed list of recipient email addresses."""
        if not self.EMAIL_TO:
            return []
        return [email.strip() for email in self.EMAIL_TO.split(",") if email.strip()]


settings = Settings()
