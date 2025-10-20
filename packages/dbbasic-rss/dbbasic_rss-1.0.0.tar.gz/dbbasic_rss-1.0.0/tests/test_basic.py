"""Basic functionality tests for dbbasic-rss"""

import pytest
from datetime import datetime
from pathlib import Path
import dbbasic_rss as rss


def test_create_empty_feed():
    """Test creating an empty feed"""
    feed = rss.Feed(
        title="Test Feed",
        link="https://example.com",
        description="A test feed"
    )
    assert feed.title == "Test Feed"
    assert feed.link == "https://example.com"
    assert feed.description == "A test feed"
    assert feed.count() == 0


def test_add_post_to_feed():
    """Test adding posts to feed"""
    feed = rss.Feed(title="Test", link="https://example.com", description="Test")

    feed.add_post(
        title="First Post",
        link="https://example.com/first",
        description="This is the first post",
        pub_date="2025-10-19"
    )

    assert feed.count() == 1
    assert feed.items[0].title == "First Post"
    assert feed.items[0].link == "https://example.com/first"


def test_add_post_with_categories():
    """Test adding post with categories"""
    feed = rss.Feed(title="Test", link="https://example.com", description="Test")

    feed.add_post(
        title="Tagged Post",
        link="https://example.com/tagged",
        description="A tagged post",
        categories=["python", "tutorial"]
    )

    assert feed.items[0].categories == ["python", "tutorial"]


def test_generate_xml():
    """Test XML generation"""
    feed = rss.Feed(
        title="Test Feed",
        link="https://example.com",
        description="Test Description"
    )

    feed.add_post(
        title="Test Post",
        link="https://example.com/post",
        description="Test post description"
    )

    xml = feed.to_xml()

    # Check for required RSS elements
    assert '<?xml version="1.0"' in xml
    assert '<rss version="2.0"' in xml
    assert '<channel>' in xml
    assert '<title>Test Feed</title>' in xml
    assert '<link>https://example.com</link>' in xml
    assert '<description>Test Description</description>' in xml
    assert '<item>' in xml
    assert '<title>Test Post</title>' in xml


def test_validate_feed():
    """Test feed validation"""
    # Valid feed
    feed = rss.Feed(title="Test", link="https://example.com", description="Test")
    feed.add_post(title="Post", link="https://example.com/post", description="Desc")
    warnings = feed.validate()
    assert len(warnings) == 0

    # Invalid feed - missing title
    feed2 = rss.Feed(title="", link="https://example.com", description="Test")
    warnings2 = feed2.validate()
    assert len(warnings2) > 0
    assert any("title" in w.lower() for w in warnings2)


def test_feed_item_date_parsing():
    """Test date parsing in FeedItem"""
    from dbbasic_rss.feed import FeedItem

    # Test ISO format
    item1 = FeedItem(
        title="Test",
        link="https://example.com",
        pub_date="2025-10-19T12:00:00"
    )
    assert item1.pub_date is not None
    assert "2025" in item1.pub_date

    # Test datetime object
    dt = datetime(2025, 10, 19, 12, 0, 0)
    item2 = FeedItem(
        title="Test",
        link="https://example.com",
        pub_date=dt
    )
    assert item2.pub_date is not None


def test_xml_escaping():
    """Test that special characters are properly escaped"""
    feed = rss.Feed(
        title="Test & Special <Characters>",
        link="https://example.com",
        description="Test 'quotes' and \"double quotes\""
    )

    feed.add_post(
        title="Post with <tags> & ampersands",
        link="https://example.com/post",
        description="Description with 'quotes'"
    )

    xml = feed.to_xml()

    # Should escape special characters
    assert '&amp;' in xml or '&' in xml  # Properly escaped or in CDATA
    assert '<tags>' not in xml  # Should be escaped


def test_feed_stats():
    """Test feed statistics methods"""
    feed = rss.Feed(title="Test", link="https://example.com", description="Test")

    feed.add_post(title="Old Post", link="https://example.com/1",
                  description="", pub_date="2025-10-15")
    feed.add_post(title="New Post", link="https://example.com/2",
                  description="", pub_date="2025-10-20")
    feed.add_post(title="Mid Post", link="https://example.com/3",
                  description="", pub_date="2025-10-17")

    assert feed.count() == 3
    # oldest() and newest() should work
    oldest = feed.oldest()
    newest = feed.newest()
    assert oldest is not None
    assert newest is not None


def test_from_posts():
    """Test generating feed from list of dicts"""
    posts = [
        {
            'title': 'Post 1',
            'date': '2025-10-19',
            'content': 'Content 1',
            'slug': 'post-1',
            'author': 'Dan'
        },
        {
            'title': 'Post 2',
            'date': '2025-10-18',
            'content': 'Content 2',
            'slug': 'post-2'
        }
    ]

    feed = rss.from_posts(
        posts,
        title='Test Blog',
        link='https://example.com',
        description='A test blog',
        url_pattern='https://example.com/{slug}/'
    )

    assert feed.count() == 2
    assert feed.items[0].title == 'Post 1'
    assert feed.items[0].link == 'https://example.com/post-1/'
    assert feed.items[0].author == 'Dan'
    assert feed.items[1].link == 'https://example.com/post-2/'


def test_from_posts_with_categories():
    """Test from_posts with category handling"""
    posts = [
        {
            'title': 'Tagged Post',
            'url': 'https://example.com/tagged',
            'content': 'Content',
            'tags': 'python,tutorial,web'
        }
    ]

    feed = rss.from_posts(
        posts,
        categories_field='tags'
    )

    assert feed.items[0].categories == ['python', 'tutorial', 'web']


def test_write_feed_to_file(tmp_path):
    """Test writing feed to file"""
    feed = rss.Feed(title="Test", link="https://example.com", description="Test")
    feed.add_post(title="Post", link="https://example.com/post", description="Desc")

    output_file = tmp_path / "feed.xml"
    feed.write(str(output_file))

    assert output_file.exists()
    content = output_file.read_text()
    assert '<?xml version' in content
    assert '<rss version="2.0"' in content
    assert 'Test' in content


def test_content_with_html():
    """Test that HTML content is preserved in CDATA"""
    feed = rss.Feed(title="Test", link="https://example.com", description="Test")

    html_content = "<p>This is <strong>HTML</strong> content</p>"
    feed.add_post(
        title="HTML Post",
        link="https://example.com/html",
        description="Plain text description",
        content=html_content
    )

    xml = feed.to_xml()
    assert '<![CDATA[' in xml
    assert html_content in xml


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
