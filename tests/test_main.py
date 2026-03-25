import sqlite3
from sqlite3 import OperationalError

import pytest
from fastapi.testclient import TestClient

from app.database import get_db_path
from app.main import app


def override_db(path: str):
    def _override() -> str:
        return path
    return _override


@pytest.fixture
def client(db_path):
    app.dependency_overrides[get_db_path] = override_db(db_path)
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_url(db_path, client):
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO urls (url) VALUES (?)", ("evil.com:8080/malware/download",))
    conn.commit()
    conn.close()
    return client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_known_malicious_url_returns_unsafe(client_with_url):
    response = client_with_url.get("/urlinfo/1/evil.com:8080/malware/download")
    assert response.status_code == 200
    assert response.json() == {"safe": False}


def test_unknown_url_returns_safe(client):
    response = client.get("/urlinfo/1/unknown.com/some/path")
    assert response.status_code == 200
    assert response.json() == {"safe": True}


def test_empty_path_is_valid(client):
    response = client.get("/urlinfo/1/example.com/")
    assert response.status_code == 200
    assert response.json() == {"safe": True}


def test_hostname_and_hostname_with_port_are_distinct(db_path, client):
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO urls (url) VALUES (?)", ("evil.com/path",))
    conn.commit()
    conn.close()
    response = client.get("/urlinfo/1/evil.com:9000/path")
    assert response.json() == {"safe": True}


def test_multi_segment_path(client_with_url):
    response = client_with_url.get("/urlinfo/1/evil.com:8080/malware/download")
    assert response.status_code == 200
    assert response.json() == {"safe": False}


def test_db_error_returns_503(monkeypatch, client):
    def broken_lookup(url, db_path=None):
        raise OperationalError("no such table: urls")

    monkeypatch.setattr("app.main.is_url_malicious", broken_lookup)
    response = client.get("/urlinfo/1/example.com/path")
    assert response.status_code == 503


def test_unexpected_error_returns_500(monkeypatch, client):
    def broken_lookup(url, db_path=None):
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr("app.main.is_url_malicious", broken_lookup)
    response = client.get("/urlinfo/1/example.com/path")
    assert response.status_code == 500


def test_404_still_works(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
