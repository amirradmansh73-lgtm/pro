from fastapi.testclient import TestClient
from netbeacon.app import app

client = TestClient(app)


def test_dashboard_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "NetBeacon" in response.text


def test_get_status_api():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "targets" in data
    assert "count" in data
