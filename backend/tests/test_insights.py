from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_team_insights():
    r = client.get("/api/v1/insights/teams?range=week")
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list) and len(items) >= 5  # 4 teams + 1 company
    first = items[0]
    assert {"id", "scope", "title", "summary", "recommendation", "severity", "category", "confidence", "tags", "createdAt", "range"}.issubset(first.keys())