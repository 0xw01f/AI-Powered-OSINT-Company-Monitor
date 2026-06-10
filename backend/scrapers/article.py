"""Article scraper using Playwright and BeautifulSoup."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

_CONTENT_SELECTORS = [
    'article',
    'main',
    '[class*="article-content"]',
    '[class*="post-content"]',
    '[class*="entry-content"]',
    '[class*="story-body"]',
    '.content',
    '#content',
]

# Minimum characters to consider extracted text valid
_MIN_CONTENT_LENGTH = 200
_MIN_FALLBACK_LENGTH = 100


def extract_text_from_html(html: str) -> str | None:
    """Extract clean article text from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html, 'lxml')

    for selector in _CONTENT_SELECTORS:
        element = soup.select_one(selector)
        if element is not None:
            text = element.get_text(separator='\n', strip=True)
            if len(text) >= _MIN_CONTENT_LENGTH:
                return text

    body = soup.find('body')
    if body is None:
        return None

    for tag_name in ('nav', 'footer', 'header', 'aside', 'script', 'style', 'noscript'):
        for tag in body.find_all(tag_name):
            tag.decompose()

    text = body.get_text(separator='\n', strip=True)
    return text if len(text) >= _MIN_FALLBACK_LENGTH else None


def scrape_article(url: str, timeout: int = 30000) -> str | None:
    """Scrape article content from URL using Playwright."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=timeout, wait_until='networkidle')
            html = page.content()
            browser.close()
    except PlaywrightTimeout:
        logger.warning('Timeout scraping %s', url)
        return None
    except Exception:
        logger.exception('Error scraping %s', url)
        return None
    return extract_text_from_html(html)
