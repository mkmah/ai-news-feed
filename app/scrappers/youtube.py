import asyncio
from datetime import timezone
import feedparser
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Optional


class Video(BaseModel):
    id: str
    title: str
    published: datetime
    link: str
    description: str
    transcript: Optional[str] = None


def get_rss_url(channel_id: str) -> str:
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def extract_video_id(url: str) -> str:
    if "video.com/watch/?v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "video.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url


async def get_latest_videos(channel_id: str, hours: int = 24) -> List[Video]:
    # feedparser is blocking, run in thread
    feed = await asyncio.to_thread(feedparser.parse, get_rss_url(channel_id))
    if not feed.entries:
        return []

    cut_off_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    videos: List[Video] = []

    for entry in feed.entries:
        video_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        if video_date > cut_off_time:
            videos.append(
                Video(
                    id=extract_video_id(entry.link),
                    title=entry.title,
                    published=video_date,
                    link=entry.link,
                    description=entry.description,
                )
            )

    return videos


async def scrape_channel(channel_id: str, hours: int = 24) -> List[Video]:
    videos = await get_latest_videos(channel_id, hours)
    return videos


if __name__ == "__main__":
    import time

    async def main():
        start = time.time()
        # Test with a specific channel
        videos = await scrape_channel(channel_id="UC0m81bQuthaQZmFbXEY9QSw", hours=48)
        end = time.time()
        print(f"Scraped {len(videos)} videos in {end - start:.2f} seconds")
        for video in videos:
            print(
                f"ID: {video.id}, Title: {video.title}, Transcript Length: {len(video.transcript) if video.transcript else 0}"
            )

    asyncio.run(main())
