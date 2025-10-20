"""Core RSS Feed and Item classes"""

from datetime import datetime
from typing import Optional, List, Dict, Any


class FeedItem:
    """Represents a single RSS feed item (article/post)"""

    def __init__(
        self,
        title: str,
        link: str,
        description: str = "",
        content: Optional[str] = None,
        pub_date: Optional[str] = None,
        guid: Optional[str] = None,
        author: Optional[str] = None,
        categories: Optional[List[str]] = None,
        enclosure: Optional[Dict[str, str]] = None,
    ):
        """
        Create a feed item.

        Args:
            title: Article title
            link: Article URL
            description: Short description/summary
            content: Full HTML content (optional)
            pub_date: Publication date (ISO format or datetime)
            guid: Unique identifier (uses link if not provided)
            author: Author name
            categories: List of category/tag names
            enclosure: Media attachment dict with 'url', 'type', 'length' (for podcasts)
        """
        self.title = title
        self.link = link
        self.description = description
        self.content = content
        self.pub_date = self._parse_date(pub_date) if pub_date else None
        self.guid = guid or link
        self.author = author
        self.categories = categories or []
        self.enclosure = enclosure

    def _parse_date(self, date_input):
        """Parse various date formats to RFC 822 format for RSS"""
        if isinstance(date_input, datetime):
            return date_input.strftime("%a, %d %b %Y %H:%M:%S GMT")

        if isinstance(date_input, str):
            # Try parsing ISO format
            try:
                dt = datetime.fromisoformat(date_input.replace('Z', '+00:00'))
                return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
            except ValueError:
                # If already in RSS format, return as-is
                return date_input

        return None


class Feed:
    """Main RSS Feed class"""

    def __init__(
        self,
        title: str = "RSS Feed",
        link: str = "",
        description: str = "",
        language: str = "en",
        author: Optional[str] = None,
        author_email: Optional[str] = None,
        image_url: Optional[str] = None,
        image_title: Optional[str] = None,
        image_link: Optional[str] = None,
        ttl: Optional[int] = None,
        category: Optional[str] = None,
    ):
        """
        Create an RSS feed.

        Args:
            title: Feed title
            link: Feed/site URL
            description: Feed description
            language: Language code (default: 'en')
            author: Author/creator name
            author_email: Author email
            image_url: Feed image/logo URL
            image_title: Image title (defaults to feed title)
            image_link: Image link (defaults to feed link)
            ttl: Time-to-live in minutes (cache duration)
            category: Feed category
        """
        self.title = title
        self.link = link
        self.description = description
        self.language = language
        self.author = author
        self.author_email = author_email
        self.image_url = image_url
        self.image_title = image_title or title
        self.image_link = image_link or link
        self.ttl = ttl
        self.category = category
        self.items: List[FeedItem] = []
        self.build_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    def add_item(self, item: FeedItem) -> None:
        """Add a FeedItem to the feed"""
        self.items.append(item)

    def add_post(
        self,
        title: str,
        link: str,
        description: str = "",
        **kwargs
    ) -> FeedItem:
        """
        Convenience method to add a post without creating FeedItem manually.

        Args:
            title: Article title
            link: Article URL
            description: Short description
            **kwargs: Additional FeedItem arguments (content, pub_date, author, etc.)

        Returns:
            The created FeedItem
        """
        item = FeedItem(title=title, link=link, description=description, **kwargs)
        self.add_item(item)
        return item

    def count(self) -> int:
        """Return number of items in feed"""
        return len(self.items)

    def oldest(self) -> Optional[str]:
        """Return oldest publication date"""
        dates = [item.pub_date for item in self.items if item.pub_date]
        return min(dates) if dates else None

    def newest(self) -> Optional[str]:
        """Return newest publication date"""
        dates = [item.pub_date for item in self.items if item.pub_date]
        return max(dates) if dates else None

    def to_xml(self) -> str:
        """
        Generate RSS 2.0 XML.

        Returns:
            RSS XML as string
        """
        from .templates import render_rss
        return render_rss(self)

    def write(self, filepath: str, format: str = "rss") -> None:
        """
        Write feed to file.

        Args:
            filepath: Output file path
            format: 'rss' or 'atom' (currently only RSS supported)
        """
        if format != "rss":
            raise NotImplementedError(f"Format '{format}' not yet implemented")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_xml())

    def validate(self) -> List[str]:
        """
        Validate feed structure and return list of warnings.

        Returns:
            List of warning messages (empty if valid)
        """
        warnings = []

        if not self.title:
            warnings.append("Feed title is missing")
        if not self.link:
            warnings.append("Feed link is missing")
        if not self.description:
            warnings.append("Feed description is missing")

        for i, item in enumerate(self.items):
            if not item.title:
                warnings.append(f"Item {i}: title is missing")
            if not item.link:
                warnings.append(f"Item {i}: link is missing")

        return warnings

    def serve(self, request) -> Any:
        """
        Flask/Django helper: Auto-detect browser vs feed reader.

        Args:
            request: Flask request or Django request object

        Returns:
            Appropriate response (XML for readers, could be HTML for browsers)

        Example:
            @app.route('/rss')
            def rss_feed():
                feed = Feed(...)
                return feed.serve(request)
        """
        # Try to detect user agent
        user_agent = ""
        if hasattr(request, 'headers'):
            user_agent = request.headers.get('User-Agent', '').lower()
        elif hasattr(request, 'META'):
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()

        # Check if it's a browser (not a feed reader)
        is_browser = any(browser in user_agent for browser in [
            'mozilla', 'chrome', 'safari', 'edge', 'opera'
        ]) and 'feed' not in user_agent and 'rss' not in user_agent

        # Generate XML
        xml_content = self.to_xml()

        # Return appropriate response based on framework
        if hasattr(request, 'app'):  # Flask
            from flask import Response
            if is_browser:
                # Could render HTML preview here in the future
                return Response(xml_content, mimetype='application/rss+xml')
            return Response(xml_content, mimetype='application/rss+xml')
        else:  # Django or other
            from django.http import HttpResponse
            return HttpResponse(xml_content, content_type='application/rss+xml')
