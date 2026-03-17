from collections.abc import Generator
from pathlib import Path

import pytest
from django.test import Client, override_settings

TEST_APP_DOCS = Path(__file__).resolve().parent.parent / "test-app" / "md-docs"

TEST_APP_SETTINGS = dict(
    MD_DOCS_DIR=TEST_APP_DOCS,
    MD_DOCS_LOGIN_REQUIRED=True,
    MD_DOCS_BRAND="My Project Docs",
    MD_DOCS_LOGOUT_URL="/accounts/logout/",
    ROOT_URLCONF="test_app.urls",
    LOGIN_URL="/accounts/login/",
)


@pytest.fixture()
def md_docs_dir(tmp_path: Path) -> Path:
    docs = tmp_path / "md-docs"
    docs.mkdir()

    (docs / "index.md").write_text("# Home\n\nWelcome.")
    (docs / "guide.md").write_text("# Guide\n\nContent here.")

    section = docs / "api"
    section.mkdir()
    (section / "index.md").write_text("# API\n\nAPI overview.")
    (section / "endpoints.md").write_text("# Endpoints\n\nEndpoint list.")

    return docs


@pytest.fixture()
def test_app_client(client: Client) -> Generator[Client, None, None]:
    with override_settings(**TEST_APP_SETTINGS):
        yield client


@pytest.fixture()
def auth_test_app_client(admin_client: Client) -> Generator[Client, None, None]:
    with override_settings(**TEST_APP_SETTINGS):
        yield admin_client
