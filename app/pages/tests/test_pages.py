import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import main_app

ACCOUNT_URL = "/api/v1/account/"


@pytest.fixture
def client():
    return TestClient(main_app)


def test_account_page_renders(client):
    """Account page returns HTML with the sign-in / sign-up UI."""

    r = client.get(ACCOUNT_URL, cookies={"locale": "en"})

    assert r.status_code == status.HTTP_200_OK
    assert "Sign in" in r.text
    assert "Sign up" in r.text
    assert "Continue with Google" in r.text
    # external assets, not inline
    assert "css/style.css" in r.text
    assert "js/auth.js" in r.text


def test_account_page_localized_ru(client):
    """Account page is translated when the locale cookie is Russian."""

    r = client.get(ACCOUNT_URL, cookies={"locale": "ru"})

    assert r.status_code == status.HTTP_200_OK
    assert 'lang="ru"' in r.text
    assert "Войти через Google" in r.text
    assert "Sign in" not in r.text
