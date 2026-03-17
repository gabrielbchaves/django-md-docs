from pathlib import Path

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.test import override_settings

from md_docs.views import _build_nav, _get_content_dir, _resolve_md_file


def test_get_content_dir_uses_md_docs_dir(tmp_path: Path) -> None:
    """MD_DOCS_DIR setting is returned as the resolved content directory."""
    with override_settings(MD_DOCS_DIR=tmp_path):
        assert _get_content_dir() == tmp_path.resolve()


def test_get_content_dir_falls_back_to_base_dir(tmp_path: Path) -> None:
    """Falls back to BASE_DIR/md-docs when MD_DOCS_DIR is not set."""
    with override_settings(MD_DOCS_DIR=None, BASE_DIR=tmp_path):
        assert _get_content_dir() == (tmp_path / "md-docs").resolve()


def test_get_content_dir_raises_without_base_dir() -> None:
    """Raises ImproperlyConfigured when neither MD_DOCS_DIR nor BASE_DIR is set."""
    with override_settings(MD_DOCS_DIR=None, BASE_DIR=None):
        with pytest.raises(ImproperlyConfigured):
            _get_content_dir()


def test_resolve_md_file_index(md_docs_dir: Path) -> None:
    """Empty slug resolves to index.md."""
    assert _resolve_md_file(md_docs_dir, "") == md_docs_dir / "index.md"


def test_resolve_md_file_direct(md_docs_dir: Path) -> None:
    """A plain slug resolves to the matching .md file."""
    assert _resolve_md_file(md_docs_dir, "guide") == md_docs_dir / "guide.md"


def test_resolve_md_file_section_index(md_docs_dir: Path) -> None:
    """A trailing-slash slug resolves to the section index.md."""
    assert _resolve_md_file(md_docs_dir, "api/") == md_docs_dir / "api" / "index.md"


def test_resolve_md_file_nested(md_docs_dir: Path) -> None:
    """A nested slug resolves to the correct file inside a subdirectory."""
    assert _resolve_md_file(md_docs_dir, "api/endpoints") == md_docs_dir / "api" / "endpoints.md"


def test_resolve_md_file_path_traversal_raises(md_docs_dir: Path) -> None:
    """Path traversal outside the content directory raises Http404."""
    with pytest.raises(Http404):
        _resolve_md_file(md_docs_dir, "../../etc/passwd")


def test_build_nav_excludes_root_index(md_docs_dir: Path) -> None:
    """Root index.md is excluded from the nav list."""
    urls = [item["url"] for item in _build_nav(md_docs_dir)]

    assert "/docs/" not in urls
    assert all("/docs/" in u for u in urls)


def test_build_nav_titles_from_headings(md_docs_dir: Path) -> None:
    """Nav titles are extracted from the first heading of each file."""
    titles = {item["title"] for item in _build_nav(md_docs_dir)}

    assert "Guide" in titles
    assert "API" in titles
    assert "Endpoints" in titles


def test_build_nav_depth_padding(md_docs_dir: Path) -> None:
    """Nav items have padding proportional to their nesting depth."""
    by_title = {item["title"]: item for item in _build_nav(md_docs_dir)}

    assert by_title["Guide"]["padding_left"] == 20
    assert by_title["API"]["padding_left"] == 20
    assert by_title["Endpoints"]["padding_left"] == 40


def test_build_nav_title_falls_back_to_stem(md_docs_dir: Path) -> None:
    """File stem is used as title when the file has no headings."""
    (md_docs_dir / "noheading.md").write_text("")
    titles = {item["title"] for item in _build_nav(md_docs_dir)}

    assert "noheading" in titles
