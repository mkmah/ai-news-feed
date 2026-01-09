from datetime import timedelta, timezone, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import YouTubeVideo, OpenAIArticle, AnthropicArticle, Digest
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

    async def get_articles_without_digest(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        articles = []
        seen_ids = set()

        result = await self.session.execute(select(Digest))
        digests = result.scalars().all()
        for d in digests:
            seen_ids.add(f"{d.article_type}:{d.article_id}")

        result = await self.session.execute(
            select(YouTubeVideo).filter(
                YouTubeVideo.transcript.isnot(None),
                YouTubeVideo.transcript != "__UNAVAILABLE__",
            )
        )
        youtube_videos = result.scalars().all()
        for video in youtube_videos:
            key = f"youtube:{video.video_id}"
            if key not in seen_ids:
                articles.append(
                    {
                        "type": "youtube",
                        "id": video.video_id,
                        "title": video.title,
                        "url": video.url,
                        "content": video.transcript or video.description or "",
                        "published_at": video.published_at,
                    }
                )

        result = await self.session.execute(select(OpenAIArticle))
        openai_articles = result.scalars().all()
        for article in openai_articles:
            key = f"openai:{article.guid}"
            if key not in seen_ids:
                articles.append(
                    {
                        "type": "openai",
                        "id": article.guid,
                        "title": article.title,
                        "url": article.url,
                        "content": article.description or "",
                        "published_at": article.published_at,
                    }
                )

        result = await self.session.execute(
            select(AnthropicArticle).filter(AnthropicArticle.markdown.isnot(None))
        )
        anthropic_articles = result.scalars().all()
        for article in anthropic_articles:
            key = f"anthropic:{article.guid}"
            if key not in seen_ids:
                articles.append(
                    {
                        "type": "anthropic",
                        "id": article.guid,
                        "title": article.title,
                        "url": article.url,
                        "content": article.markdown or article.description or "",
                        "published_at": article.published_at,
                    }
                )

        if limit:
            articles = articles[:limit]

        return articles

    async def create_digest(
        self,
        article_type: str,
        article_id: str,
        url: str,
        title: str,
        summary: str,
        published_at: Optional[datetime] = None,
    ) -> Optional[Digest]:
        digest_id = f"{article_type}:{article_id}"
        result = await self.session.execute(select(Digest).filter_by(id=digest_id))
        existing = result.scalars().first()
        if existing:
            return None

        if published_at:
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            created_at = published_at
        else:
            created_at = datetime.now(timezone.utc)

        digest = Digest(
            id=digest_id,
            article_type=article_type,
            article_id=article_id,
            url=url,
            title=title,
            summary=summary,
            created_at=created_at,
        )
        self.session.add(digest)
        await self.session.commit()
        return digest

    async def get_recent_digests(self, hours: int = 24) -> List[Dict[str, Any]]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        digests = await self.session.execute(
            select(Digest)
            .filter(Digest.created_at >= cutoff_time)
            .order_by(Digest.created_at.desc())
        )
        digests = digests.scalars().all()
        return [
            {
                "id": d.id,
                "article_type": d.article_type,
                "article_id": d.article_id,
                "url": d.url,
                "title": d.title,
                "summary": d.summary,
                "created_at": d.created_at,
            }
            for d in digests
        ]
