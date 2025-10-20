"""Tests for data source generators"""

import pytest
from pathlib import Path
import dbbasic_rss as rss


FIXTURES_DIR = Path(__file__).parent / 'fixtures'


def test_from_csv():
    """Test generating feed from CSV file"""
    csv_file = FIXTURES_DIR / 'sample.csv'

    feed = rss.from_csv(
        str(csv_file),
        title='CSV Blog',
        link='https://example.com',
        description='From CSV'
    )

    assert feed.count() == 2
    assert feed.items[0].title == 'First Post'
    assert feed.items[0].link == 'https://example.com/first'


def test_from_json():
    """Test generating feed from JSON file"""
    json_file = FIXTURES_DIR / 'sample.json'

    feed = rss.from_json(
        str(json_file),
        title='JSON Blog',
        link='https://example.com',
        description='From JSON'
    )

    assert feed.count() == 2
    assert feed.items[0].title == 'JSON Post 1'
    assert feed.items[0].author == 'Test Author'


def test_from_tsv():
    """Test generating feed from TSV file"""
    tsv_file = FIXTURES_DIR / 'sample.tsv'

    feed = rss.from_tsv(
        str(tsv_file),
        title='TSV Blog',
        link='https://example.com',
        description='From TSV',
        url_pattern='https://example.com/{slug}/',
        categories_field='tags'
    )

    assert feed.count() == 3
    assert feed.items[0].title == 'Getting Started with Python'
    assert feed.items[0].link == 'https://example.com/getting-started-python/'
    assert feed.items[0].author == 'Dan Quellhorst'
    assert 'python' in feed.items[0].categories
    assert 'tutorial' in feed.items[0].categories


def test_generate_auto_detect_tsv(tmp_path):
    """Test generate() auto-detecting TSV format"""
    tsv_file = FIXTURES_DIR / 'sample.tsv'
    output_file = tmp_path / 'output.xml'

    rss.generate(
        str(tsv_file),
        str(output_file),
        title='Auto-detected',
        link='https://example.com',
        url_pattern='https://example.com/{slug}/'
    )

    assert output_file.exists()
    content = output_file.read_text()
    assert 'Getting Started with Python' in content
    assert '<rss version="2.0"' in content


def test_generate_auto_detect_csv(tmp_path):
    """Test generate() auto-detecting CSV format"""
    csv_file = FIXTURES_DIR / 'sample.csv'
    output_file = tmp_path / 'output.xml'

    rss.generate(
        str(csv_file),
        str(output_file),
        title='CSV Auto',
        link='https://example.com'
    )

    assert output_file.exists()
    content = output_file.read_text()
    assert 'First Post' in content


def test_generate_auto_detect_json(tmp_path):
    """Test generate() auto-detecting JSON format"""
    json_file = FIXTURES_DIR / 'sample.json'
    output_file = tmp_path / 'output.xml'

    rss.generate(
        str(json_file),
        str(output_file),
        title='JSON Auto',
        link='https://example.com'
    )

    assert output_file.exists()
    content = output_file.read_text()
    assert 'JSON Post 1' in content


def test_generate_unsupported_format():
    """Test that unsupported formats raise error"""
    with pytest.raises(ValueError, match="Unsupported file format"):
        rss.generate('file.txt', 'output.xml')


def test_url_pattern_substitution():
    """Test URL pattern field substitution"""
    posts = [
        {'title': 'Test', 'id': '123', 'slug': 'test-post', 'content': 'Content'}
    ]

    feed = rss.from_posts(
        posts,
        url_pattern='https://example.com/posts/{id}/{slug}/'
    )

    assert feed.items[0].link == 'https://example.com/posts/123/test-post/'


def test_custom_field_mapping():
    """Test custom field name mapping"""
    posts = [
        {
            'headline': 'Custom Title',
            'published_date': '2025-10-19',
            'body': 'Post body',
            'permalink': 'https://example.com/custom'
        }
    ]

    feed = rss.from_posts(
        posts,
        title_field='headline',
        date_field='published_date',
        content_field='body',
        url_field='permalink'
    )

    assert feed.items[0].title == 'Custom Title'
    assert feed.items[0].link == 'https://example.com/custom'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
