# Getting Started

## Installation

```bash
pip install django-md-docs
```

## Configuration

Add `md_docs` to `INSTALLED_APPS` and include its URLs:

```python
# settings.py
INSTALLED_APPS = [
    ...
    "md_docs",
]

MD_DOCS_BRAND = "My Project"
MD_DOCS_LOGIN_REQUIRED = True
MD_DOCS_LOGOUT_URL = "/accounts/logout/"
```

```python
# urls.py
urlpatterns = [
    path("docs/", include("md_docs.urls")),
]
```

## File layout

Place your `.md` files under `BASE_DIR/md-docs/`:

```
md-docs/
├── index.md
├── getting-started.md
└── api/
    ├── index.md
    └── endpoints.md
```
