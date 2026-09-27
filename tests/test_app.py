import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import app


def test_health():
    c = app.test_client()
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json["status"] == "ok"


def test_demo():
    c = app.test_client()
    r = c.get("/api/demo")
    assert r.status_code == 200
    assert r.json["project_name"] == "Retail Portal"
    assert len(r.json["test_catalog"]) >= 5


def test_app_id_route():
    c = app.test_client()
    r = c.get("/local/api/demo")
    assert r.status_code == 200
    assert "test_catalog" in r.json


def test_playwright_generation():
    c = app.test_client()
    r = c.post("/api/generate-playwright", json={"test_url": "https://example.com", "scenarios": [{"title": "Payment timeout recovery"}]})
    assert r.status_code == 200
    assert "@playwright/test" in r.json["generated_test"]
