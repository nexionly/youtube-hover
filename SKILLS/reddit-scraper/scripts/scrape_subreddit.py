#!/usr/bin/env python3
"""
Scrape top posts from any subreddit using Reddit's public JSON API.

Usage:
    python scrape_subreddit.py <subreddit> [--count N] [--time FILTER] [--json]

Examples:
    python scrape_subreddit.py customersuccess
    python scrape_subreddit.py python --count 5 --time week
    python scrape_subreddit.py news --count 10 --time day --json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def scrape_subreddit(subreddit: str, count: int = 3, time_filter: str = "all") -> list[dict]:
    """
    Fetch the top `count` posts from r/{subreddit}.

    Args:
        subreddit:   Subreddit name (without r/ prefix).
        count:       Number of posts to retrieve (max 100).
        time_filter: One of: hour, day, week, month, year, all.

    Returns:
        List of dicts with post metadata.
    """
    url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={count}&t={time_filter}"
    req = Request(url, headers={"User-Agent": "reddit-scraper-skill/1.0 (educational)"})

    with urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())

    posts = []
    for child in data.get("data", {}).get("children", []):
        d = child["data"]
        posts.append({
            "rank": len(posts) + 1,
            "title": d.get("title"),
            "author": d.get("author"),
            "score": d.get("score"),
            "upvote_ratio": d.get("upvote_ratio"),
            "num_comments": d.get("num_comments"),
            "created_utc": datetime.fromtimestamp(
                d.get("created_utc", 0), tz=timezone.utc
            ).isoformat(),
            "url": d.get("url"),
            "permalink": f"https://reddit.com{d.get('permalink', '')}",
            "selftext_preview": (d.get("selftext") or "")[:300] or None,
            "is_self": d.get("is_self"),
            "flair": d.get("link_flair_text"),
        })
    return posts


def print_posts(posts: list[dict], subreddit: str) -> None:
    """Pretty-print posts to terminal."""
    print(f"\n{'=' * 70}")
    print(f"  Top {len(posts)} posts from r/{subreddit}")
    print(f"{'=' * 70}\n")
    for p in posts:
        print(f"  #{p['rank']}  {p['title']}")
        print(f"     Author: u/{p['author']}  |  Score: {p['score']}  |  Comments: {p['num_comments']}")
        print(f"     Upvote ratio: {p['upvote_ratio']}  |  Posted: {p['created_utc']}")
        if p["flair"]:
            print(f"     Flair: {p['flair']}")
        print(f"     Link: {p['permalink']}")
        if p["selftext_preview"]:
            print(f"     Preview: {p['selftext_preview'].replace(chr(10), ' ')}...")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape top posts from a subreddit.")
    parser.add_argument("subreddit", help="Subreddit name (without r/ prefix)")
    parser.add_argument("--count", "-n", type=int, default=3, help="Number of posts (default: 3)")
    parser.add_argument("--time", "-t", default="all",
                        choices=["hour", "day", "week", "month", "year", "all"],
                        help="Time filter (default: all)")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON to stdout")
    args = parser.parse_args()

    log = sys.stderr if args.json else sys.stdout
    print(f"🔍  Scraping r/{args.subreddit} (top {args.count}, time={args.time})…", file=log)

    try:
        posts = scrape_subreddit(args.subreddit, args.count, args.time)
    except HTTPError as e:
        print(f"❌  HTTP {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except URLError:
        print("❌  Connection failed. Check your internet.", file=sys.stderr)
        sys.exit(1)

    if not posts:
        print(f"⚠️  No posts found in r/{args.subreddit}.", file=log)
        sys.exit(0)

    if args.json:
        print(json.dumps(posts, indent=2, ensure_ascii=False))
    else:
        print_posts(posts, args.subreddit)

    print(f"✅  Scraped {len(posts)} posts.", file=log)


if __name__ == "__main__":
    main()
