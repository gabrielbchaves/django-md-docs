import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_anonymous_redirected_to_login(test_app_client: Client) -> None:
    """Unauthenticated requests are redirected to the login page."""
    response = test_app_client.get("/docs/")

    assert response.status_code == 302
    assert "/login/" in response["Location"]


def test_index_renders(auth_test_app_client: Client) -> None:
    """The docs index page returns 200 and renders the welcome content."""
    response = auth_test_app_client.get("/docs/")

    assert response.status_code == 200
    assert b"Welcome" in response.content


def test_brand_in_index(auth_test_app_client: Client) -> None:
    """The configured brand name appears in the rendered page."""
    response = auth_test_app_client.get("/docs/")

    assert b"My Project Docs" in response.content


def test_logout_button_in_index(auth_test_app_client: Client) -> None:
    """The logout URL is rendered in the sidebar when configured."""
    response = auth_test_app_client.get("/docs/")

    assert b"/accounts/logout/" in response.content


def test_getting_started_renders(auth_test_app_client: Client) -> None:
    """The getting-started page returns 200 and renders its content."""
    response = auth_test_app_client.get("/docs/getting-started")

    assert response.status_code == 200
    assert b"Installation" in response.content


def test_api_section_index_renders(auth_test_app_client: Client) -> None:
    """The api/ section index page returns 200 and renders its content."""
    response = auth_test_app_client.get("/docs/api/")

    assert response.status_code == 200
    assert b"Authentication" in response.content


def test_api_endpoints_renders(auth_test_app_client: Client) -> None:
    """The api/endpoints page returns 200 and renders its content."""
    response = auth_test_app_client.get("/docs/api/endpoints")

    assert response.status_code == 200
    assert b"GET /api/items/" in response.content


def test_unknown_page_returns_404(auth_test_app_client: Client) -> None:
    """A slug with no matching file returns 404."""
    response = auth_test_app_client.get("/docs/does-not-exist")

    assert response.status_code == 404


def test_nav_contains_all_pages(auth_test_app_client: Client) -> None:
    """All markdown pages are listed in the navigation sidebar."""
    content = auth_test_app_client.get("/docs/").content.decode()

    assert "Getting Started" in content
    assert "API" in content
    assert "Endpoints" in content


def test_active_nav_link_highlighted(auth_test_app_client: Client) -> None:
    """The nav link matching the current page has the active class."""
    response = auth_test_app_client.get("/docs/getting-started")

    assert b'class="active"' in response.content


def test_toc_rendered_for_multi_heading_page(auth_test_app_client: Client) -> None:
    """Pages with multiple headings render a table of contents sidebar."""
    response = auth_test_app_client.get("/docs/getting-started")

    assert b"toc-sidebar" in response.content


def test_path_traversal_blocked(auth_test_app_client: Client) -> None:
    """Path traversal attempts outside the docs directory are blocked."""
    response = auth_test_app_client.get("/docs/../../etc/passwd")

    assert response.status_code in (404, 400)


def test_markdown_table_renders_as_html_table(auth_test_app_client: Client) -> None:
    """Markdown tables are converted to <table> HTML elements."""
    response = auth_test_app_client.get("/docs/api/endpoints")

    assert b"<table>" in response.content
    assert b"<thead>" in response.content
    assert b"<th>" in response.content
    assert b"<td>" in response.content


def test_fenced_code_block_renders_as_pre_code(auth_test_app_client: Client) -> None:
    """Fenced code blocks are converted to <pre><code> HTML elements."""
    response = auth_test_app_client.get("/docs/getting-started")

    assert b"<pre>" in response.content
    assert b"<code>" in response.content


def test_headings_render_as_h_tags(auth_test_app_client: Client) -> None:
    """Markdown headings are converted to the correct <h1>/<h2> HTML elements."""
    response = auth_test_app_client.get("/docs/getting-started")

    assert b'<h1 id="getting-started">Getting Started</h1>' in response.content
    assert b'<h2 id="installation">Installation</h2>' in response.content


def test_bold_text_renders_as_strong(auth_test_app_client: Client) -> None:
    """Bold markdown syntax is converted to <strong> HTML elements."""
    response = auth_test_app_client.get("/docs/")

    assert b"<strong>My Project Docs</strong>" in response.content


def test_toc_links_have_anchors(auth_test_app_client: Client) -> None:
    """Headings in pages with ToC get id attributes for anchor links."""
    response = auth_test_app_client.get("/docs/getting-started")

    assert b'href="#installation"' in response.content


def test_section_index_without_trailing_slash_redirects(
    auth_test_app_client: Client,
) -> None:
    """Visiting a section index without a trailing slash redirects permanently to the slash URL."""
    response = auth_test_app_client.get("/docs/api")

    assert response.status_code == 301
    assert response["Location"] == "/docs/api/"
