"""
Python FastAPI-based GitHub webhook receiver.

validation functions.
"""

import hmac
import hashlib
from fastapi import Request, status
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from .config import WEBHOOK_SECRET, MAX_PAYLOAD_SIZE


def verify_signature(signature, data) -> bool:
    """
    Verifies the HMAC SHA-256 signature of a GitHub webhook event.

    This function ensures the authenticity and integrity of the webhook payload
    by comparing the provided 'X-Hub-Signature-256' header value with a computed
    HMAC digest of the request body using the shared webhook secret.

    Parameters:
        signature (str): The value of the 'X-Hub-Signature-256' header from the request.
                         This should be in the format 'sha256=<HMAC_HEX_DIGEST>'.
        body (bytes): The raw request body received from GitHub.

    Returns:
        bool: True if the signature is valid and matches the computed digest, False otherwise.

    Raises:
        None: Any exceptions (e.g., malformed input) should be handled by the caller."""
    expected_signature = (
        "sha256=" + hmac.new(WEBHOOK_SECRET.encode(), data, hashlib.sha256).hexdigest()
    )
    return hmac.compare_digest(signature, expected_signature)


# pylint: disable=too-few-public-methods
class ContentLengthLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce a maximum Content-Length on incoming HTTP requests.

    This middleware checks the 'Content-Length' header for requests with methods
    that typically include a body (POST, PUT, PATCH). If the header is missing or
    indicates a size greater than the allowed maximum, the request is rejected with
    an appropriate HTTP error response:

    - 411 Length Required: if the header is missing
    - 400 Bad Request: if the header is not a valid integer
    - 413 Payload Too Large: if the size exceeds the defined limit

    Requests using methods like GET, DELETE, or OPTIONS are not subject to this check.

    Attributes:
        MAX_PAYLOAD_SIZE (int): The maximum allowed payload size in bytes.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Validate Content-Length for requests with a body.
        If the Content-Length header is not present, it returns a 411 Length Required response.

        :param request: The incoming request
        :param call_next: The next function to call in the middleware chain
        :return: The response to return to the client
        """
        if request.method in {"POST", "PUT", "PATCH"}:
            content_length = request.headers.get("Content-Length")
            if content_length:
                try:
                    size = int(content_length)
                    if size > MAX_PAYLOAD_SIZE:
                        return JSONResponse(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            content={
                                "detail": f"Payload too large. Maximum size is {MAX_PAYLOAD_SIZE} bytes."
                            },
                        )
                except ValueError:
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "detail": "Invalid Content-Length header: content_length is not a valid integer."
                        },
                    )
            else:
                return JSONResponse(
                    status_code=status.HTTP_411_LENGTH_REQUIRED,
                    content={"detail": "Content-Length header is required."},
                )
        response = await call_next(request)
        return response
