from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_trend_default():
    r = client.get("/api/v1/dashboard/trend")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) > 0
    assert {"date", "label", "avgSentiment", "messageCount"}.issubset(data[0].keys())


def test_channels_and_kpi():
    r = client.get("/api/v1/dashboard/channels")
    assert r.status_code == 200
    channels = r.json()
    assert isinstance(channels, list) and len(channels) > 0

    r2 = client.get("/api/v1/dashboard/kpi")
    assert r2.status_code == 200
    kpi = r2.json()
    assert set(kpi.keys()) == {"avgSentiment", "burnoutRiskCount", "monitoredChannels"}