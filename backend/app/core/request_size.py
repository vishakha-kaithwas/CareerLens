"""
ASGI Middleware for early request size limit enforcement.

Guarantees that oversized request payloads are rejected BEFORE:
1. Starlette/FastAPI parses multipart form data.
2. Python's SpooledTemporaryFile overflows and writes bytes to temporary disk.
"""

import json
import logging
from starlette.types import ASGIApp, Receive, Scope, Send
from app.core.config import settings

logger = logging.getLogger("careerlens.middleware.request_size")


class RequestSizeLimitMiddleware:
    """
    ASGI middleware that inspects Content-Length headers and counts raw streaming
    chunks. If the incoming request exceeds max_body_size_bytes, it immediately
    halts consumption and responds with HTTP 413 Payload Too Large (or HTTP 400),
    preventing any multipart parser from spooling bytes to disk.
    """

    def __init__(self, app: ASGIApp, max_body_size_bytes: int):
        self.app = app
        self.max_body_size = max_body_size_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length_header = headers.get(b"content-length")

        # 1. Fast-path: Check Content-Length header upfront if provided by client
        if content_length_header is not None:
            try:
                content_length = int(content_length_header.decode("latin-1"))
                if content_length > self.max_body_size:
                    logger.warning(
                        "Request Content-Length (%d bytes) exceeds max body size (%d bytes). Rejecting early.",
                        content_length,
                        self.max_body_size,
                    )
                    await self._send_size_exceeded_response(send, content_length)
                    return
            except (ValueError, UnicodeDecodeError):
                pass  # Fall through to stream counting if header is malformed

        # 2. Defensive streaming counter: Wraps receive() to count bytes in real-time
        # Protects against missing or spoofed Content-Length headers (e.g. Transfer-Encoding: chunked)
        total_bytes_received = 0

        async def counting_receive():
            nonlocal total_bytes_received
            message = await receive()
            if message["type"] == "http.request":
                chunk = message.get("body", b"")
                total_bytes_received += len(chunk)
                if total_bytes_received > self.max_body_size:
                    logger.warning(
                        "Streaming request exceeded max body size (%d bytes). Rejecting early.",
                        self.max_body_size,
                    )
                    # Note: We send the response directly on send
                    raise RequestSizeExceededException(total_bytes_received)
            return message

        try:
            await self.app(scope, counting_receive, send)
        except RequestSizeExceededException as exc:
            await self._send_size_exceeded_response(send, exc.total_bytes)

    async def _send_size_exceeded_response(self, send: Send, bytes_received: int) -> None:
        limit_mb = self.max_body_size / (1024 * 1024)
        payload = {
            "success": False,
            "message": f"Request payload exceeds the maximum allowed request size of {limit_mb:.2f} MB.",
            "data": None,
            "errors": {
                "max_allowed_bytes": self.max_body_size,
                "bytes_received": bytes_received,
                "type": "request_payload_too_large",
            },
        }
        body = json.dumps(payload).encode("utf-8")

        await send({
            "type": "http.response.start",
            "status": 413,  # Payload Too Large
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("latin-1")),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })


class RequestSizeExceededException(Exception):
    """Internal sentinel exception when stream counting exceeds limit."""
    def __init__(self, total_bytes: int):
        self.total_bytes = total_bytes
