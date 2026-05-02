---
name: reddit-scraper
description: Scrape top posts from any Reddit subreddit. Use when the user wants to fetch, analyze, or monitor Reddit posts from a specific subreddit. Triggers include requests like "scrape r/python", "get top posts from the sales subreddit", "what's trending on r/news", or "pull Reddit posts about customer success".
---

# Reddit Scraper

Scrape top posts from any subreddit using Reddit's public JSON API. No API keys or authentication required.

## Quick Start

Run the bundled script with the target subreddit as a positional argument:

```bash
python3 scripts/scrape_subreddit.py <subreddit> [--count N] [--time FILTER] [--json]
```

**Arguments:**

| Arg | Default | Description |
|---|---|---|
| `subreddit` | *(required)* | Subreddit name without `r/` prefix |
| `--count`, `-n` | `3` | Number of posts to fetch (max 100) |
| `--time`, `-t` | `all` | Time filter: `hour`, `day`, `week`, `month`, `year`, `all` |
| `--json`, `-j` | off | Output raw JSON to stdout (status goes to stderr) |

**Examples:**

```bash
# Top 3 all-time from r/customersuccess
python3 scripts/scrape_subreddit.py customersuccess

# Top 5 posts this week from r/python, as JSON
python3 scripts/scrape_subreddit.py python --count 5 --time week --json
```

## Dependencies

**None** — uses only Python stdlib (`urllib`, `json`). No `pip install` needed.

## Data Returned Per Post

Each post object contains: `rank`, `title`, `author`, `score`, `upvote_ratio`, `num_comments`, `created_utc` (ISO 8601), `url`, `permalink`, `selftext_preview` (first 300 chars), `is_self`, `flair`.

## Workflow

1. Ask the user which subreddit to scrape (and optionally count / time filter).
2. Run the script from the skill directory.
3. Present results to the user, or pipe the `--json` output into further processing.

## Limitations

- Reddit rate-limits unauthenticated requests; avoid rapid repeated calls.
- Maximum 100 posts per request (Reddit API limit).
- Private or quarantined subreddits may return errors.
