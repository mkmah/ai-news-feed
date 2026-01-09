import asyncio
from app.runner import run_daily_pipeline


async def main(hours: int = 24, top_n: int = 10):
    results = await run_daily_pipeline(hours=hours, top_n=top_n)
    return results


if __name__ == "__main__":

    async def cli_entrypoint():
        import sys

        hours = 24
        top_n = 10

        if len(sys.argv) > 1:
            hours = int(sys.argv[1])
        if len(sys.argv) > 2:
            top_n = int(sys.argv[2])

        result = await main(hours=hours, top_n=top_n)
        exit(0 if result["success"] else 1)

    asyncio.run(cli_entrypoint())
