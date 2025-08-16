from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_slack_connection():
    r = client.get("/api/v1/slack/connection")
    assert r.status_code == 200
    data = r.json()
    assert set(data.keys()) >= {"teamId", "teamName", "isConnected"}


def test_slack_channels_and_users():
    rc = client.get("/api/v1/slack/channels")
    assert rc.status_code == 200
    channels = rc.json()
    assert isinstance(channels, list) and len(channels) > 0

    ru = client.get("/api/v1/slack/users")
    assert ru.status_code == 200
    users = ru.json()
    assert isinstance(users, list) and len(users) > 0
