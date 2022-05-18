from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)


def test_read_server():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"GoTo": "/docs"}


def test_prediction():
    response = client.post(
        "/housing_area_prediction",
        json={
            "single": 0.0,
            "married_no_kids": 0.0,
            "not_marred_no_kids": 0.0,
            "married_w_kids": 0.0,
            "not_married_w_kids": 0.0,
            "single_parent": 0.0,
            "other": 0.0,
            "total": 0.0,
            "area_code": "string"
        },
    )
    response_json = response.json()
    assert response.status_code == 200
    assert len(response_json.keys()) == 1
    assert type(response_json['predicted woz price']) == float
