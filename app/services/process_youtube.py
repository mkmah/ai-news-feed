import asyncio
from app.db.connection import get_session
from typing import Optional
from app.scrapers.youtube import YoutubeScraper
from app.db.repo import Repository

TRANSCRIPT_UNAVAILABLE_MARKER = "__UNAVAILABLE__"


async def process_youtube_transcripts(limit: Optional[int] = None) -> dict:
    scraper = YoutubeScraper()

    processed = 0
    unavailable = 0
    failed = 0
    videos = []

    async with get_session() as session:
        repo = Repository(session=session)

        videos = await repo.get_youtube_videos_without_transcript(limit=limit)

        for video in videos:
            try:
                transcript_result = await scraper.get_transcript(video.video_id)
                if transcript_result:
                    if not await repo.update_youtube_video_transcript(
                        video.video_id, transcript_result.text
                    ):
                        raise Exception("Failed to update transcript")
                    processed += 1
                else:
                    if not await repo.update_youtube_video_transcript(
                        video.video_id, TRANSCRIPT_UNAVAILABLE_MARKER
                    ):
                        raise Exception("Failed to update transcript")
                    unavailable += 1
            except Exception as e:
                # if not await repo.update_youtube_video_transcript(video.video_id, TRANSCRIPT_UNAVAILABLE_MARKER):
                # raise Exception("Failed to update transcript")
                failed += 1
                print(f"Error processing video {video.video_id}: {e}")

    return {
        "total": len(videos),
        "processed": processed,
        "unavailable": unavailable,
        "failed": failed,
    }


if __name__ == "__main__":

    async def main():
        result = await process_youtube_transcripts()
        print(f"Total videos: {result['total']}")
        print(f"Processed: {result['processed']}")
        print(f"Unavailable: {result['unavailable']}")
        print(f"Failed: {result['failed']}")

    asyncio.run(main())
