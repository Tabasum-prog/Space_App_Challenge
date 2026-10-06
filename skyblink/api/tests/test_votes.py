from fastapi.testclient import TestClient
from api.app.main import app

client = TestClient(app)

def test_votes():
    response = client.post("/votes", json={"candidate_id": "c1", "vote": "real"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
