# AI News Feed Aggregator

I built this tool to help me keep up with the fast-paced world of Artificial Intelligence without getting overwhelmed. Instead of constantly checking multiple websites and YouTube channels, I run this pipeline to automatically scrape, summarize, and curate the most relevant updates for me.

It's essentially a personal news assistant that looks at YouTube transcripts, OpenAI's blog, and Anthropic's research, and then sends a consolidated digest directly to my inbox.

## How It Works

The system runs a pipeline that performs several steps:

1.  **Scraping**: It connects to various sources to fetch the latest content.
    *   **YouTube**: Fetches the latest videos from specified channels and downloads their transcripts.
    *   **OpenAI & Anthropic**: Monitors their RSS feeds for new blog posts and research papers, converting the HTML content into clean Markdown.
2.  **Digesting**: An AI agent reads through the articles and transcripts, generating concise summaries and extracting the key points.
3.  **Curation**: Another agent ranks the digests based on relevance and quality to ensure the most important news bubbles to the top.
4.  **Delivery**: Finally, it formats the top stories into an email and sends it out.

## Tech Stack

The project is built with Python 3.12+ and uses a few key libraries:
*   `asyncio` & `aiohttp` for efficient, non-blocking network operations.
*   `FastAPI` / `SQLAlchemy` (asyncpg) for database interactions.
*   `Pydantic` for data validation and settings management.
*   `html_to_markdown` for content processing.
*   `YouTube Transcript API` for getting youtube video transcript.

## Getting Started

If you want to run this yourself, you'll need Python installed and a PostgreSQL database running.

### 1. Environment Setup

Create a `.env` file in the `app` directory (or root, depending on how you run it) with your configuration.

```ini
# Database (Required)
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=ai_news_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# AI Services
OPENAI_API_KEY=sk-...

# Email Configuration (for sending the digest)
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_app_password

# Optional: YouTube Proxy (if running in data centers)
YOUTUBE_PROXY_USERNAME=user
YOUTUBE_PROXY_PASSWORD=pass
```

### 2. Dependencies

I use `uv` for package management, which is significantly faster than pip.

```bash
uv sync
```

### 3. Start Database

Start the PostgreSQL database container.

```bash
make db
```

### 4. Run Migrations

Apply the database schema migrations.

```bash
make migrate
```

## Usage

To run the pipeline manually:

```bash
uv run -m app.main
```

You can also specify arguments to control the lookback period and the number of articles in the digest:

```bash
# Get news from the last 48 hours and include the top 5 stories
uv run -m app.main 48 5
```

## Project Structure

*   `app/scrapers`: Contains the logic for fetching data from YouTube, OpenAI, etc.
*   `app/services`: Business logic for processing emails, digests, and ranking.
*   `app/agents`: The AI agents responsible for summarization and curation.
*   `app/db`: Database models and connection logic.
*   `app/runner.py`: The main orchestration script that ties everything together.
