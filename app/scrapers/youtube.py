from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
import asyncio
from datetime import timezone
import feedparser
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Optional


class YoutubeVideo(BaseModel):
    video_id: str
    title: str
    published_at: datetime
    link: str
    description: str
    channel_id: str
    transcript: Optional[str] = None


class YoutubeScraper:
    def __init__(self):
        self.ytt_api = YouTubeTranscriptApi()

    def _get_rss_url(self, channel_id: str) -> str:
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    def _extract_video_id(self, url: str) -> str:
        if "video.com/watch/?v=" in url:
            return url.split("v=")[1].split("&")[0]
        if "youtube.com/shorts/" in url:
            return url.split("shorts/")[1].split("?")[0]
        if "video.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        return url

    async def get_latest_videos(
        self, channel_id: str, hours: int = 24
    ) -> List[YoutubeVideo]:
        # feedparser is blocking, run in thread
        feed = await asyncio.to_thread(feedparser.parse, self._get_rss_url(channel_id))
        if not feed.entries:
            return []

        cut_off_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        videos: List[YoutubeVideo] = []

        for entry in feed.entries:
            if "/shorts/" in entry.link:
                continue

            video_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            if video_date > cut_off_time:
                videos.append(
                    YoutubeVideo(
                        video_id=self._extract_video_id(entry.link),
                        title=entry.title,
                        published_at=video_date,
                        link=entry.link,
                        description=entry.description,
                        channel_id=channel_id,
                    )
                )

        return videos

    async def _get_transcript(video_id: str) -> Optional[str]:
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript = await asyncio.to_thread(ytt_api.fetch, video_id)
            return " ".join([snippet.text for snippet in transcript.snippets])
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except Exception:
            return None

    async def scrape_channel(
        self, channel_id: str, hours: int = 24
    ) -> List[YoutubeVideo]:
        videos = await self._get_latest_videos(channel_id, hours)

        tasks = [self._get_transcript(video.video_id) for video in videos]

        transcripts = await asyncio.gather(*tasks)

        for video, transcript in zip(videos, transcripts):
            video.transcript = transcript

        return videos


if __name__ == "__main__":
    import time

    async def main():
        start = time.time()
        youtube = YoutubeScraper()
        # Test with a specific channel
        videos = await youtube.scrape_channel(
            channel_id="UC0m81bQuthaQZmFbXEY9QSw", hours=48
        )
        end = time.time()
        print(f"Scraped {len(videos)} videos in {end - start:.2f} seconds")
        for video in videos:
            print(
                f"ID: {video.video_id}, Title: {video.title}, Transcript Length: {len(video.transcript) if video.transcript else 0}"
            )

    asyncio.run(main())
