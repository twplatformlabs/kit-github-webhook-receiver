import hmac
import hashlib
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.validation import verify_signature, ContentLengthLimiterMiddleware
from api.config import WEBHOOK_SECRET, MAX_PAYLOAD_SIZE


def test_verify_signature_valid():
    data = b'{"test": "value"}'
    signature = (
        "sha256=" + hmac.new(WEBHOOK_SECRET.encode(), data, hashlib.sha256).hexdigest()
    )
    assert verify_signature(signature, data) is True


def test_verify_signature_invalid():
    data = b'{"test": "value"}'
    fake_signature = "sha256=" + "0" * 64
    assert verify_signature(fake_signature, data) is False


@pytest.fixture
def app_with_middleware():
    app = FastAPI()

    app.add_middleware(ContentLengthLimiterMiddleware)

    @app.post("/test")
    async def test_endpoint():
        return {"message": "OK"}

    return app


def test_invalid_content_length(app_with_middleware):
    client = TestClient(app_with_middleware)
    response = client.post("/test", content=b"data", headers={"Content-Length": "abc"})
    assert response.status_code == 400
    assert "Invalid Content-Length" in response.json()["detail"]


def test_payload_too_large(app_with_middleware):
    client = TestClient(app_with_middleware)
    large_content = b"x" * (MAX_PAYLOAD_SIZE + 1)
    response = client.post("/test", content=large_content)
    assert response.status_code == 413
    assert "Payload too large" in response.json()["detail"]


def test_valid_payload(app_with_middleware):
    client = TestClient(app_with_middleware)
    valid_content = b"hello"
    response = client.post("/test", content=valid_content)
    assert response.status_code == 200
    assert response.json()["message"] == "OK"
