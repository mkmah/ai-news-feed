import asyncio
from typing import Optional
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)


async def get_transcript(video_id: str) -> Optional[str]:
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = await asyncio.to_thread(ytt_api.fetch, video_id)
        return " ".join([snippet.text for snippet in transcript.snippets])
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception:
        return None


if __name__ == "__main__":
    import time

    async def main():
        start = time.time()
        # Test with a specific channel
        transcript = await get_transcript("cyeg3A5FV8E")
        end = time.time()
        print(f"{end - start:.2f} seconds")
        print(transcript)

    asyncio.run(main())
