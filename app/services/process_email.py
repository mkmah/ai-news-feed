import asyncio
from app.db.connection import get_session
import logging

from app.agents.email import EmailAgent
from app.agents.curator import CuratorAgent
from app.profiles.user_profile import USER_PROFILE
from app.db.repo import Repository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def generate_email_digest(hours: int = 24, top_n: int = 10) -> dict:
    curator = CuratorAgent(USER_PROFILE)
    email_agent = EmailAgent(USER_PROFILE)

    async with get_session() as session:
        repo = Repository(session=session)

        digests = await repo.get_recent_digests(hours=hours)
        total = len(digests)

        if total == 0:
            logger.warning(f"No digests found from the last {hours} hours")
            return {"error": "No digests available"}

        logger.info(f"Ranking {total} digests for email generation")
        ranked_articles = await curator.rank_digests(digests)

        if not ranked_articles:
            logger.error("Failed to rank digests")
            return {"error": "Failed to rank articles"}

        logger.info(f"Generating email digest with top {top_n} articles")

        email_digest = await email_agent.create_email_digest(
            ranked_articles=[
                {
                    "digest_id": a.digest_id,
                    "rank": a.rank,
                    "relevance_score": a.relevance_score,
                    "reasoning": a.reasoning,
                    "title": next(
                        (d["title"] for d in digests if d["id"] == a.digest_id), ""
                    ),
                    "summary": next(
                        (d["summary"] for d in digests if d["id"] == a.digest_id), ""
                    ),
                    "url": next(
                        (d["url"] for d in digests if d["id"] == a.digest_id), ""
                    ),
                    "article_type": next(
                        (d["article_type"] for d in digests if d["id"] == a.digest_id),
                        "",
                    ),
                }
                for a in ranked_articles
            ],
            limit=top_n,
        )

        logger.info("Email digest generated successfully")
        logger.info("\n=== Email Introduction ===")
        logger.info(email_digest.introduction.greeting)
        logger.info(f"\n{email_digest.introduction.introduction}")

        return {
            "introduction": {
                "greeting": email_digest.introduction.greeting,
                "introduction": email_digest.introduction.introduction,
            },
            "articles": email_digest.ranked_articles,
            "total_ranked": len(ranked_articles),
            "top_n": top_n,
        }


if __name__ == "__main__":

    async def main():
        result = await generate_email_digest(hours=24, top_n=10)

        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("\n=== Email Digest Generated ===")
            print(f"\n{result['introduction']['greeting']}")
            print(f"\n{result['introduction']['introduction']}")
            print(f"\nTop {result['top_n']} articles:")
            for article in result["articles"]:
                print(
                    f"\n{article['rank']}. {article['title']} (Score: {article['relevance_score']:.1f}/10)"
                )
                print(f"   {article['summary'][:100]}...")

    asyncio.run(main())
