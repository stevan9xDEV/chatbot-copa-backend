from unittest.mock import patch

import pytest

from app import create_app
from routes.chat import conversations


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    conversations.clear()
    return app.test_client()


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


@patch("routes.chat.GroqService")
def test_valid_chat(mock_service, client):
    mock_service.return_value.generate_response.return_value = "O Brasil venceu em 2002."
    response = client.post("/api/chat", json={"message": "Quem ganhou em 2002?"})
    assert response.status_code == 200
    assert "response" in response.get_json()
    assert "conversation_id" in response.get_json()


def test_empty_message(client):
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422


def test_long_message(client):
    response = client.post("/api/chat", json={"message": "A" * 5001})
    assert response.status_code == 422


def test_invalid_json(client):
    response = client.post("/api/chat", data='{"message": ', content_type="application/json")
    assert response.status_code == 400
    assert response.get_json()["message"] == "JSON inválido."


def test_missing_api_key(client):
    from services.groq_service import GroqAuthenticationError

    with patch("routes.chat.GroqService", side_effect=GroqAuthenticationError()):
        response = client.post("/api/chat", json={"message": "Olá"})
    assert response.status_code == 401


def test_groq_rate_limit(client):
    from services.groq_service import GroqRateLimitError

    service = patch("routes.chat.GroqService")
    with service as mock:
        mock.return_value.generate_response.side_effect = GroqRateLimitError()
        response = client.post("/api/chat", json={"message": "Olá"})
    assert response.status_code == 429


def test_groq_error(client):
    from services.groq_service import GroqServiceError

    with patch("routes.chat.GroqService") as mock:
        mock.return_value.generate_response.side_effect = GroqServiceError()
        response = client.post("/api/chat", json={"message": "Olá"})
    assert response.status_code == 500
