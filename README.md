# django-md-docs

A reusable Django app that renders a folder of Markdown files as a documentation site at `/docs`.

## Installation

```bash
pip install django-md-docs
```

## Setup

**1. `settings.py`**

```python
INSTALLED_APPS = [
    ...
    "md_docs",
]

# Optional settings (all have defaults):
MD_DOCS_DIR = BASE_DIR / "md-docs"        # default: BASE_DIR / "md-docs"
MD_DOCS_LOGIN_REQUIRED = True              # default: True
MD_DOCS_BRAND = "My Project"              # default: "Documentation"
MD_DOCS_LOGOUT_URL = "/accounts/logout/"  # default: None (hides the logout button)
```

**2. `urls.py`**

```python
from django.urls import include, path

urlpatterns = [
    ...
    path("docs/", include("md_docs.urls")),
]
```

**3. Create your markdown files**

```
md-docs/
├── index.md          →  /docs/
├── guide/
│   ├── index.md      →  /docs/guide/
│   └── setup.md      →  /docs/guide/setup
└── api/
    ├── index.md      →  /docs/api/
    └── endpoints.md  →  /docs/api/endpoints
```

The navigation sidebar is built automatically from the directory structure. The first heading in each file is used as its nav label.

## Settings reference

| Setting | Default | Description |
|---|---|---|
| `MD_DOCS_DIR` | `BASE_DIR / "md-docs"` | Path to the folder containing `.md` files |
| `MD_DOCS_LOGIN_REQUIRED` | `True` | Redirect unauthenticated users to `LOGIN_URL` |
| `MD_DOCS_BRAND` | `"Documentation"` | Brand name displayed in the sidebar header |
| `MD_DOCS_LOGOUT_URL` | `None` | URL for the logout POST action. When `None`, the logout button is hidden |

## Supported Markdown extensions

- `tables`
- `fenced_code`
- `toc` (table of contents, shown in the right sidebar)
- `attr_list`
