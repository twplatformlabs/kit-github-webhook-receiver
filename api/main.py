"""
Python FastAPI-based GitHub webhook receiver.
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from .routes import healthz
from .config import settings, route_prefix
from .validation import verify_signature, ContentLengthLimiterMiddleware
from .actions import on_push

tags_metadata = [{"name": "main"}]

api = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.releaseId,
    openapi_tags=tags_metadata,
    docs_url=f"{route_prefix}/apidocs",
    openapi_url=f"{route_prefix}/openapi.json",
    redoc_url=None,
    debug=settings.debug,
)

api.add_middleware(ContentLengthLimiterMiddleware)
api.include_router(healthz.route, prefix=route_prefix)


@api.post(
    route_prefix,
    summary="webhook receiver",
    tags=["main"],
    status_code=status.HTTP_202_ACCEPTED,
)
async def root(request: Request) -> JSONResponse:
    """
    GitHub webhook entrypoint.

    Validates incoming POST requests using HMAC signature via X-Hub-Signature-256.
    Dispatches supported GitHub events such as push or pull request events.
    """
    signature = request.headers.get("X-Hub-Signature-256")
    data = await request.body()

    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Hub-Signature-256 header",
        )

    if not verify_signature(signature, data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: action",
        )

    payload = await request.json()

    # Process the webhook payload for supported response options
    match payload:
        case {"ref": _, **_rest} if "ref_type" not in payload:
            on_push(payload)

        # TODO: Implement handlers for other GitHub events as needed
        # case {"action": "opened", "pull_request": _, **_rest}:
        #     on_pull_request(payload)
        # case {"action": "opened", "issue": _, **_rest}:
        #     on_issue_create(payload)
        # case {"ref": _, "ref_type": _, **_rest}:
        #     on_tag(payload)
        # case {"action": "created", "repository": _, **_rest}:
        #     on_repository_create(payload)

    return {"message": "Webhook received successfully"}


FastAPIInstrumentor.instrument_app(api)
