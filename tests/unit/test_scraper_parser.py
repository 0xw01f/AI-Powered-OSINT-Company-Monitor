"""Unit tests for the HTML text extraction parser."""

from __future__ import annotations

from backend.scrapers.article import extract_text_from_html


class TestExtractTextFromHtml:
    """Test suite for extract_text_from_html."""

    def test_article_tag_priority(self) -> None:
        """Content inside <article> should be extracted when present."""
        html = (
            '<html><body><article><p>Hello world this is a very long article '
            'that needs to be at least two hundred characters long so we are '
            'adding a lot of filler text here to make sure it passes the threshold</p>'
            '</article></body></html>'
        )
        result = extract_text_from_html(html)
        assert result is not None
        assert 'Hello world' in result

    def test_main_tag_fallback(self) -> None:
        """Content inside <main> should be used when <article> is absent."""
        html = (
            '<html><body><main><p>Main content here that is definitely longer '
            'than two hundred characters so that it passes the minimum length '
            'check and gets extracted properly by the beautiful soup parser</p>'
            '</main></body></html>'
        )
        result = extract_text_from_html(html)
        assert result is not None
        assert 'Main content here' in result

    def test_body_fallback(self) -> None:
        """Body content should be used when no specific container matches."""
        html = (
            '<html><body><div><p>Fallback text paragraph that is very long and '
            'must exceed one hundred characters to be accepted by the body fallback '
            'extractor because the minimum threshold is set quite high</p></div></body></html>'
        )
        result = extract_text_from_html(html)
        assert result is not None
        assert 'Fallback text paragraph' in result

    def test_too_short_returns_none(self) -> None:
        """Text shorter than minimum threshold should return None."""
        html = '<html><body><p>Short</p></body></html>'
        result = extract_text_from_html(html)
        assert result is None

    def test_removes_nav_footer_header(self) -> None:
        """Navigation, footer and header elements should be stripped."""
        html = (
            '<html><body>'
            '<nav>Menu item</nav>'
            '<header>Site header</header>'
            '<main>Real article content that is long enough to pass the threshold '
            'because it needs to be at least two hundred characters long</main>'
            '<footer>Copyright 2024</footer>'
            '</body></html>'
        )
        result = extract_text_from_html(html)
        assert result is not None
        assert 'Real article content' in result
        assert 'Menu item' not in result
        assert 'Site header' not in result
        assert 'Copyright 2024' not in result

    def test_removes_scripts_and_styles(self) -> None:
        """Script and style tags should not appear in extracted text."""
        html = (
            '<html><body>'
            '<script>alert("xss")</script>'
            '<style>.red{color:red}</style>'
            '<article>Clean text that is definitely longer than two hundred '
            'characters so that it passes the minimum length check easily</article>'
            '</body></html>'
        )
        result = extract_text_from_html(html)
        assert result is not None
        assert 'Clean text' in result
        assert 'alert' not in result
        assert '.red' not in result

    def test_empty_html_returns_none(self) -> None:
        """Empty HTML should return None."""
        result = extract_text_from_html('')
        assert result is None

    def test_none_body_returns_none(self) -> None:
        """HTML without body tag should return None."""
        result = extract_text_from_html('<html><head><title>Title</title></head></html>')
        assert result is None
