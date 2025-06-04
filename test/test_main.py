import httpx
import hmac
import hashlib
import json
import pytest
from api.main import api
from api.config import WEBHOOK_SECRET, route_prefix


@pytest.mark.asyncio
async def test_webhook_missing_signature():
    transport = httpx.ASGITransport(app=api)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            route_prefix, content=b"{}", headers={"Content-Length": "2"}
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing X-Hub-Signature-256 header"


@pytest.mark.asyncio
async def test_webhook_invalid_signature():
    transport = httpx.ASGITransport(app=api)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            route_prefix,
            content=b"{}",
            headers={
                "X-Hub-Signature-256": "sha256=" + "0" * 64,
                "Content-Length": "2",
            },
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing required field: action"


@pytest.mark.asyncio
async def test_webhook_valid_signature():
    payload = {"action": "opened"}
    data = json.dumps(payload).encode()
    signature = (
        "sha256=" + hmac.new(WEBHOOK_SECRET.encode(), data, hashlib.sha256).hexdigest()
    )

    transport = httpx.ASGITransport(app=api)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            route_prefix,
            content=data,
            headers={
                "X-Hub-Signature-256": signature,
                "Content-Length": str(len(data)),
            },
        )
    assert response.status_code == 202
    assert response.json()["message"] == "Webhook received successfully"
