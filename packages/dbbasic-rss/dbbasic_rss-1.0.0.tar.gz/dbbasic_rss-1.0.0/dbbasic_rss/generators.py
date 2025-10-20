"""Data source generators for RSS feeds"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from .feed import Feed, FeedItem


def from_posts(
    posts: List[Dict[str, Any]],
    title: str = "RSS Feed",
    link: str = "",
    description: str = "",
    url_pattern: Optional[str] = None,
    title_field: str = "title",
    date_field: str = "date",
    content_field: str = "content",
    description_field: Optional[str] = None,
    author_field: str = "author",
    url_field: Optional[str] = "url",
    categories_field: Optional[str] = None,
    **feed_kwargs
) -> Feed:
    """
    Generate RSS feed from list of dictionaries/objects.

    Args:
        posts: List of post dictionaries
        title: Feed title
        link: Feed URL
        description: Feed description
        url_pattern: URL pattern with {field} placeholders (e.g., 'https://site.com/{slug}/')
        title_field: Field name for post title
        date_field: Field name for publication date
        content_field: Field name for content/description
        description_field: Optional separate field for description
        author_field: Field name for author
        url_field: Field name for URL (if url_pattern not used)
        categories_field: Field name for categories (can be comma-separated string or list)
        **feed_kwargs: Additional Feed() arguments

    Returns:
        Populated Feed object

    Example:
        posts = [
            {'title': 'Post 1', 'date': '2025-10-19', 'content': 'Text...', 'slug': 'post-1'},
        ]
        feed = from_posts(posts, url_pattern='https://example.com/{slug}/')
    """
    feed = Feed(title=title, link=link, description=description, **feed_kwargs)

    for post in posts:
        # Get field values with fallbacks
        item_title = post.get(title_field, "Untitled")
        item_content = post.get(content_field, "")
        item_description = post.get(description_field) if description_field else item_content
        item_date = post.get(date_field)
        item_author = post.get(author_field)

        # Handle URL generation
        if url_pattern:
            # Replace {field} placeholders with post values
            item_url = url_pattern
            for key, value in post.items():
                item_url = item_url.replace(f'{{{key}}}', str(value))
        else:
            item_url = post.get(url_field, "")

        # Handle categories
        categories = []
        if categories_field and categories_field in post:
            cats = post[categories_field]
            if isinstance(cats, str):
                categories = [c.strip() for c in cats.split(',') if c.strip()]
            elif isinstance(cats, list):
                categories = cats

        feed.add_post(
            title=item_title,
            link=item_url,
            description=item_description,
            content=item_content if description_field else None,  # Only use content if separate description
            pub_date=item_date,
            author=item_author,
            categories=categories,
        )

    return feed


def from_tsv(
    filepath: str,
    title: str = "RSS Feed",
    link: str = "",
    description: str = "",
    url_pattern: Optional[str] = None,
    **kwargs
) -> Feed:
    """
    Generate RSS feed from TSV file.

    Args:
        filepath: Path to TSV file
        title: Feed title
        link: Feed URL
        description: Feed description
        url_pattern: URL pattern with {field} placeholders
        **kwargs: Additional arguments passed to from_posts()

    Returns:
        Populated Feed object

    Example:
        feed = from_tsv('articles.tsv',
                        title='My Blog',
                        url_pattern='https://example.com/{slug}/')
    """
    try:
        from dbbasic_tsv import TSV
        table = TSV(filepath)
        posts = table.select()
    except ImportError:
        # Fallback to standard CSV reader if dbbasic_tsv not available
        posts = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            posts = list(reader)

    return from_posts(posts, title=title, link=link, description=description,
                      url_pattern=url_pattern, **kwargs)


def from_csv(
    filepath: str,
    title: str = "RSS Feed",
    link: str = "",
    description: str = "",
    url_pattern: Optional[str] = None,
    **kwargs
) -> Feed:
    """
    Generate RSS feed from CSV file.

    Args:
        filepath: Path to CSV file
        title: Feed title
        link: Feed URL
        description: Feed description
        url_pattern: URL pattern with {field} placeholders
        **kwargs: Additional arguments passed to from_posts()

    Returns:
        Populated Feed object

    Example:
        feed = from_csv('posts.csv',
                        url_pattern='https://example.com/{id}/')
    """
    posts = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        posts = list(reader)

    return from_posts(posts, title=title, link=link, description=description,
                      url_pattern=url_pattern, **kwargs)


def from_json(
    filepath: str,
    title: str = "RSS Feed",
    link: str = "",
    description: str = "",
    url_pattern: Optional[str] = None,
    **kwargs
) -> Feed:
    """
    Generate RSS feed from JSON file.

    Args:
        filepath: Path to JSON file (should contain array of objects)
        title: Feed title
        link: Feed URL
        description: Feed description
        url_pattern: URL pattern with {field} placeholders
        **kwargs: Additional arguments passed to from_posts()

    Returns:
        Populated Feed object

    Example:
        feed = from_json('posts.json',
                         url_pattern='https://example.com/{id}/')
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        posts = json.load(f)

    if not isinstance(posts, list):
        raise ValueError("JSON file must contain an array of objects")

    return from_posts(posts, title=title, link=link, description=description,
                      url_pattern=url_pattern, **kwargs)


def from_directory(
    directory: str,
    pattern: str = "*.md",
    extract_metadata: bool = True,
    url_pattern: Optional[str] = None,
    title: str = "RSS Feed",
    link: str = "",
    description: str = "",
    **kwargs
) -> Feed:
    """
    Generate RSS feed from files in a directory.

    Args:
        directory: Directory path
        pattern: Glob pattern for files (e.g., '*.md', '*.txt')
        extract_metadata: Try to extract YAML frontmatter from files
        url_pattern: URL pattern with {filename}, {stem} placeholders
        title: Feed title
        link: Feed URL
        description: Feed description
        **kwargs: Additional arguments passed to from_posts()

    Returns:
        Populated Feed object

    Example:
        feed = from_directory('posts/',
                              pattern='*.md',
                              url_pattern='https://example.com/posts/{stem}/')
    """
    posts = []
    dir_path = Path(directory)

    for file_path in sorted(dir_path.glob(pattern), reverse=True):
        post = {
            'filename': file_path.name,
            'stem': file_path.stem,
        }

        content = file_path.read_text(encoding='utf-8')

        # Extract YAML frontmatter if requested
        if extract_metadata and content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                # Parse YAML frontmatter
                try:
                    import yaml
                    metadata = yaml.safe_load(parts[1])
                    if isinstance(metadata, dict):
                        post.update(metadata)
                    content = parts[2].strip()
                except ImportError:
                    # Fallback: simple key: value parsing
                    for line in parts[1].strip().split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            post[key.strip()] = value.strip()
                    content = parts[2].strip()

        # Set content
        post['content'] = content
        post['title'] = post.get('title', file_path.stem.replace('-', ' ').title())

        # Get file modification time as date if not in metadata
        if 'date' not in post:
            post['date'] = file_path.stat().st_mtime

        posts.append(post)

    return from_posts(posts, title=title, link=link, description=description,
                      url_pattern=url_pattern, **kwargs)


def generate(
    source: str,
    output: str,
    title: str = "RSS Feed",
    link: str = "",
    description: str = "",
    **kwargs
):
    """
    One-liner to generate RSS feed from file to file.

    Auto-detects source format from extension and generates feed.

    Args:
        source: Input file path (.tsv, .csv, .json)
        output: Output XML file path
        title: Feed title
        link: Feed URL
        description: Feed description
        **kwargs: Additional arguments

    Example:
        generate('articles.tsv', 'feed.xml', title='My Blog')
    """
    source_path = Path(source)
    ext = source_path.suffix.lower()

    # Auto-detect source type
    if ext == '.tsv':
        feed = from_tsv(source, title=title, link=link, description=description, **kwargs)
    elif ext == '.csv':
        feed = from_csv(source, title=title, link=link, description=description, **kwargs)
    elif ext == '.json':
        feed = from_json(source, title=title, link=link, description=description, **kwargs)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    feed.write(output)
