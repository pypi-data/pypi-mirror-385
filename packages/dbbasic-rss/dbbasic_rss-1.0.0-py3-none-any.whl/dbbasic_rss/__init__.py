"""
dbbasic-rss: Simple, composable RSS feed generation for Python

A Unix-philosophy approach to RSS feeds:
- Read from simple data sources (TSV, CSV, JSON, lists)
- Generate standards-compliant RSS 2.0
- Framework-agnostic (works with Flask, Django, FastAPI, static sites)
- No heavy dependencies
- Composable with dbbasic-tsv and other modules

Quick Start:
    # One-liner
    import dbbasic_rss as rss
    rss.generate('articles.tsv', 'feed.xml')

    # From TSV (works with dbbasic-tsv)
    feed = rss.from_tsv('articles.tsv',
                        title='My Blog',
                        url_pattern='https://example.com/{slug}/')
    feed.write('feed.xml')

    # From list of dicts
    posts = [{'title': 'Post 1', 'date': '2025-10-19', 'url': 'https://...'}]
    feed = rss.from_posts(posts)
    print(feed.to_xml())

    # Custom feed
    feed = rss.Feed(title='My Blog', link='https://example.com')
    feed.add_post(title='Article', link='https://example.com/article/')
    feed.write('feed.xml')
"""

from .feed import Feed, FeedItem
from .generators import (
    from_posts,
    from_tsv,
    from_csv,
    from_json,
    from_directory,
    generate,
)

__version__ = "1.0.0"
__all__ = [
    "Feed",
    "FeedItem",
    "from_posts",
    "from_tsv",
    "from_csv",
    "from_json",
    "from_directory",
    "generate",
]
