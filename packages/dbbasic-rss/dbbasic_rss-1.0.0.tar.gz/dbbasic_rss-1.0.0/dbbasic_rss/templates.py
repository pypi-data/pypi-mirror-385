"""RSS XML template rendering (pure Python, no external dependencies)"""

from typing import TYPE_CHECKING
from html import escape

if TYPE_CHECKING:
    from .feed import Feed, FeedItem


def escape_xml(text: str) -> str:
    """Escape XML special characters"""
    if text is None:
        return ""
    return escape(str(text), quote=True)


def render_item(item: 'FeedItem') -> str:
    """Render a single feed item to XML"""
    xml_parts = ['    <item>']

    # Required fields
    xml_parts.append(f'      <title>{escape_xml(item.title)}</title>')
    xml_parts.append(f'      <link>{escape_xml(item.link)}</link>')
    xml_parts.append(f'      <guid>{escape_xml(item.guid)}</guid>')

    # Description
    if item.description:
        xml_parts.append(f'      <description>{escape_xml(item.description)}</description>')

    # Content (with CDATA for HTML)
    if item.content:
        xml_parts.append(f'      <content:encoded><![CDATA[{item.content}]]></content:encoded>')

    # Publication date
    if item.pub_date:
        xml_parts.append(f'      <pubDate>{escape_xml(item.pub_date)}</pubDate>')

    # Author
    if item.author:
        xml_parts.append(f'      <dc:creator>{escape_xml(item.author)}</dc:creator>')

    # Categories
    for category in item.categories:
        xml_parts.append(f'      <category>{escape_xml(category)}</category>')

    # Enclosure (for podcasts/media)
    if item.enclosure:
        enc_url = escape_xml(item.enclosure.get('url', ''))
        enc_type = escape_xml(item.enclosure.get('type', 'audio/mpeg'))
        enc_length = escape_xml(item.enclosure.get('length', '0'))
        xml_parts.append(f'      <enclosure url="{enc_url}" type="{enc_type}" length="{enc_length}" />')

    xml_parts.append('    </item>')
    return '\n'.join(xml_parts)


def render_rss(feed: 'Feed') -> str:
    """Render complete RSS 2.0 feed"""
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']

    # RSS opening tag with namespaces
    xml_parts.append(
        '<rss version="2.0" '
        'xmlns:content="http://purl.org/rss/1.0/modules/content/" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:atom="http://www.w3.org/2005/Atom">'
    )

    xml_parts.append('  <channel>')

    # Required channel elements
    xml_parts.append(f'    <title>{escape_xml(feed.title)}</title>')
    xml_parts.append(f'    <link>{escape_xml(feed.link)}</link>')
    xml_parts.append(f'    <description>{escape_xml(feed.description)}</description>')

    # Optional channel elements
    if feed.language:
        xml_parts.append(f'    <language>{escape_xml(feed.language)}</language>')

    if feed.build_date:
        xml_parts.append(f'    <lastBuildDate>{escape_xml(feed.build_date)}</lastBuildDate>')

    if feed.ttl:
        xml_parts.append(f'    <ttl>{feed.ttl}</ttl>')

    if feed.category:
        xml_parts.append(f'    <category>{escape_xml(feed.category)}</category>')

    # Managing editor / webmaster
    if feed.author_email and feed.author:
        xml_parts.append(f'    <managingEditor>{escape_xml(feed.author_email)} ({escape_xml(feed.author)})</managingEditor>')
    elif feed.author_email:
        xml_parts.append(f'    <managingEditor>{escape_xml(feed.author_email)}</managingEditor>')

    # Atom self-reference (best practice)
    if feed.link:
        xml_parts.append(f'    <atom:link href="{escape_xml(feed.link)}" rel="self" type="application/rss+xml" />')

    # Image (logo/icon)
    if feed.image_url:
        xml_parts.append('    <image>')
        xml_parts.append(f'      <url>{escape_xml(feed.image_url)}</url>')
        xml_parts.append(f'      <title>{escape_xml(feed.image_title)}</title>')
        xml_parts.append(f'      <link>{escape_xml(feed.image_link)}</link>')
        xml_parts.append('    </image>')

    # Items
    for item in feed.items:
        xml_parts.append(render_item(item))

    xml_parts.append('  </channel>')
    xml_parts.append('</rss>')

    return '\n'.join(xml_parts)
