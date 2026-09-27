import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app import app

def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

def test_demo():
    client = app.test_client()
    response = client.get("/api/demo")
    assert response.status_code == 200
    assert "test_catalog" in response.get_json()

def test_playwright_generation():
    client = app.test_client()
    response = client.post(
        "/api/generate-playwright",
        json={"test_url":"https://example.com","scenarios":[{"title":"Open application"}]}
    )
    assert response.status_code == 200
    assert "playwright" in response.get_json()["generated_test"].lower()
