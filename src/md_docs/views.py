from pathlib import Path
from typing import Any

import markdown
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
)
from django.shortcuts import render
from django.urls import reverse


def _get_content_dir() -> Path:
    path = getattr(settings, "MD_DOCS_DIR", None)
    if path is None:
        base_dir = getattr(settings, "BASE_DIR", None)
        if base_dir is None:
            raise ImproperlyConfigured("Set MD_DOCS_DIR or BASE_DIR in settings.")
        path = Path(base_dir) / "md-docs"
    return Path(path).resolve()


def _resolve_md_file(content_dir: Path, page: str) -> Path:
    """Translate a URL slug to an absolute markdown file path.

    Raises Http404 if the resolved path escapes the content directory.
    """
    clean = page.strip("/")

    if clean == "":
        candidate = content_dir / "index.md"
    else:
        direct = (content_dir / clean).with_suffix(".md")
        candidate = direct if direct.exists() else content_dir / clean / "index.md"

    resolved = candidate.resolve()
    if not resolved.is_relative_to(content_dir):
        raise Http404

    return resolved


def _build_nav(content_dir: Path) -> list[dict[str, Any]]:
    """Walk the content directory and return an ordered nav list.

    Each entry has:
        url   - absolute URL to the page
        title - first heading found in the file (fallback: filename stem)
        depth - nesting level (0 = root, 1 = section, ...)
    """
    nav = []

    def _sort_key(p: Path) -> tuple[str, ...]:
        parts = list(p.relative_to(content_dir).parts)
        if parts[-1] == "index.md":
            parts[-1] = ""
        return tuple(parts)

    for path in sorted(content_dir.rglob("*.md"), key=_sort_key):
        rel = path.relative_to(content_dir)
        parts = rel.parts

        is_index = parts[-1] == "index.md"
        if parts == ("index.md",):
            continue

        slug = "/".join(parts[:-1]) if is_index else "/".join(parts).removesuffix(".md")
        url = (
            reverse("md_docs:docs-page", args=[slug])
            if slug
            else reverse("md_docs:docs-index")
        )

        first_line = next(
            (line for line in path.read_text().splitlines() if line.strip()), ""
        )
        title = first_line.lstrip("#").strip() or path.stem

        depth = max(0, len(parts) - 2) if is_index else len(parts) - 1
        nav.append({"url": url, "title": title, "padding_left": 20 + depth * 20})

    return nav


async def docs_page(request: HttpRequest, page: str = "") -> HttpResponse:
    """Serve a rendered markdown documentation page.

    The ``page`` slug maps to a file under the configured ``MD_DOCS_DIR``:
    - empty / ``index``     → ``<MD_DOCS_DIR>/index.md``
    - ``api/messages``      → ``<MD_DOCS_DIR>/api/messages.md``
    - ``admin/``            → ``<MD_DOCS_DIR>/admin/index.md``

    Settings
    --------
    MD_DOCS_DIR           Path to the directory containing .md files.
                          Defaults to BASE_DIR / "md-docs".
    MD_DOCS_LOGIN_REQUIRED  Restrict access to authenticated users (default True).
    MD_DOCS_BRAND         Brand name shown in the sidebar (default "Documentation").
    MD_DOCS_LOGOUT_URL    URL for the logout action. When None the logout button
                          is hidden (default None).
    """
    if (
        getattr(settings, "MD_DOCS_LOGIN_REQUIRED", True)
        and not (await request.auser()).is_authenticated
    ):
        return redirect_to_login(request.get_full_path())

    content_dir = _get_content_dir()
    md_file = _resolve_md_file(content_dir, page)
    if not md_file.exists():
        raise Http404

    if md_file.name == "index.md" and page and not page.endswith("/"):
        return HttpResponsePermanentRedirect(
            reverse("md_docs:docs-page", args=[page + "/"])
        )

    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "attr_list"],
        extension_configs={"toc": {"title": "Contents"}},
    )
    body = md.convert(md_file.read_text())

    slug = page.strip("/")
    current_url = (
        reverse("md_docs:docs-page", args=[slug])
        if slug
        else reverse("md_docs:docs-index")
    )

    return render(
        request,
        "md_docs/page.html",
        {
            "body": body,
            "toc": getattr(md, "toc", ""),
            "nav": _build_nav(content_dir),
            "current_url": current_url,
            "brand": getattr(settings, "MD_DOCS_BRAND", "Documentation"),
            "logout_url": getattr(settings, "MD_DOCS_LOGOUT_URL", None),
        },
    )
