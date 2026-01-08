from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import YouTubeVideo, OpenAIArticle, AnthropicArticle
from .connection import get_session
from app.scrapers.youtube import YoutubeVideo as PydanticYoutubeVideo
from app.scrapers.openai import OpenAIArticle as PydanticOpenAIArticle
from app.scrapers.anthropic import AnthropicArticle as PydanticAnthropicArticle


class Repository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session or get_session()

    async def create_youtube_video(
        self,
        video_id: str,
        title: str,
        url: str,
        channel_id: str,
        published_at: datetime,
        description: str = "",
        transcript: Optional[str] = None,
    ) -> Optional[YouTubeVideo]:
        result = await self.session.execute(
            select(YouTubeVideo).filter_by(video_id=video_id)
        )
        existing = result.scalars().first()
        if existing:
            return None
        video = YouTubeVideo(
            video_id=video_id,
            title=title,
            url=url,
            channel_id=channel_id,
            published_at=published_at,
            description=description,
            transcript=transcript,
        )
        self.session.add(video)
        await self.session.commit()
        return video

    async def create_openai_article(
        self,
        guid: str,
        title: str,
        url: str,
        published_at: datetime,
        description: str = "",
        category: Optional[str] = None,
    ) -> Optional[OpenAIArticle]:
        result = await self.session.execute(select(OpenAIArticle).filter_by(guid=guid))
        existing = result.scalars().first()
        if existing:
            return None
        article = OpenAIArticle(
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            description=description,
            category=category,
        )
        self.session.add(article)
        await self.session.commit()
        return article

    async def create_anthropic_article(
        self,
        guid: str,
        title: str,
        url: str,
        published_at: datetime,
        description: str = "",
        category: Optional[str] = None,
    ) -> Optional[AnthropicArticle]:
        result = await self.session.execute(
            select(AnthropicArticle).filter_by(guid=guid)
        )
        existing = result.scalars().first()
        if existing:
            return None
        article = AnthropicArticle(
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            description=description,
            category=category,
        )
        self.session.add(article)
        await self.session.commit()
        return article

    async def bulk_create_youtube_videos(
        self, videos: List[PydanticYoutubeVideo]
    ) -> int:
        new_videos = []
        for v in videos:
            result = await self.session.execute(
                select(YouTubeVideo).filter_by(video_id=v.video_id)
            )
            existing = result.scalars().first()
            if not existing:
                new_video = YouTubeVideo(
                    video_id=v.video_id,
                    title=v.title,
                    url=v.link,
                    channel_id=v.channel_id,
                    published_at=v.published_at,
                    description=v.description,
                    transcript=v.transcript,
                )
                new_videos.append(new_video)
        if new_videos:
            self.session.add_all(new_videos)
            await self.session.commit()
        return len(new_videos)

    async def bulk_create_openai_articles(
        self, articles: List[PydanticOpenAIArticle]
    ) -> int:
        new_articles = []
        for article in articles:
            result = await self.session.execute(
                select(OpenAIArticle).filter_by(guid=article.guid)
            )
            existing = result.scalars().first()
            if not existing:
                new_article = OpenAIArticle(
                    guid=article.guid,
                    title=article.title,
                    url=article.url,
                    published_at=article.published_at,
                    description=article.description,
                    category=article.category,
                )
                new_articles.append(new_article)
        if new_articles:
            self.session.add_all(new_articles)
            await self.session.commit()
        return len(new_articles)

    async def bulk_create_anthropic_articles(
        self, articles: List[PydanticAnthropicArticle]
    ) -> int:
        new_articles = []
        for article in articles:
            result = await self.session.execute(
                select(AnthropicArticle).filter_by(guid=article.guid)
            )
            existing = result.scalars().first()
            if not existing:
                new_article = AnthropicArticle(
                    guid=article.guid,
                    title=article.title,
                    url=article.url,
                    published_at=article.published_at,
                    description=article.description,
                    category=article.category,
                )
                new_articles.append(new_article)
        if new_articles:
            self.session.add_all(new_articles)
            await self.session.commit()
        return len(new_articles)

    async def get_anthropic_articles_without_markdown(
        self, limit: Optional[int] = None
    ) -> List[AnthropicArticle]:
        stmt = select(AnthropicArticle).filter(AnthropicArticle.markdown.is_(None))
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_anthropic_article_markdown(self, guid: str, markdown: str) -> bool:
        result = await self.session.execute(
            select(AnthropicArticle).filter_by(guid=guid)
        )
        article = result.scalars().first()
        if article:
            article.markdown = markdown
            await self.session.commit()
            return True
        return False

    async def get_youtube_videos_without_transcript(
        self, limit: Optional[int] = None
    ) -> List[YouTubeVideo]:
        stmt = select(YouTubeVideo).filter(YouTubeVideo.transcript.is_(None))
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_youtube_video_transcript(
        self, video_id: str, transcript: str
    ) -> bool:
        result = await self.session.execute(
            select(YouTubeVideo).filter_by(video_id=video_id)
        )
        video = result.scalars().first()
        if video:
            video.transcript = transcript
            await self.session.commit()
            return True
        return False
