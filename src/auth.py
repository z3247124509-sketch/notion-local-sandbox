"""In-memory bearer authentication; no request or credential logging."""
import asyncio
import hashlib
import hmac
import re


def bearer_digest(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{64}", value):
        raise ValueError("A user-supplied 64-character URL-safe token is required")
    if len(set(value)) < 8:
        raise ValueError("Token does not meet the local input policy")
    return hashlib.sha256(value.encode("ascii")).digest()


class Auth:
    def __init__(self, app, digest):
        self.app, self.digest, self.active = app, digest, 0

    async def reject(self, send, status):
        await send({"type": "http.response.start", "status": status,
                    "headers": [(b"content-type", b"application/json"), (b"cache-control", b"no-store")]})
        await send({"type": "http.response.body", "body": b'{"error":"request_denied"}'})

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)
        if scope["type"] != "http":
            return
        values = [v for k, v in scope["headers"] if k.lower() == b"authorization"]
        if len(values) != 1 or not re.fullmatch(rb"Bearer [A-Za-z0-9_-]{64}", values[0]):
            return await self.reject(send, 401)
        if not hmac.compare_digest(hashlib.sha256(values[0][7:]).digest(), self.digest):
            return await self.reject(send, 401)
        if scope.get("path") != "/mcp" or scope.get("query_string"):
            return await self.reject(send, 404)
        if scope["method"] not in {"POST", "GET", "DELETE"}:
            return await self.reject(send, 405)
        if self.active >= 8:
            return await self.reject(send, 429)
        self.active += 1
        try:
            body = bytearray()
            try:
                async with asyncio.timeout(5):
                    while True:
                        event = await receive()
                        if event["type"] == "http.disconnect":
                            return
                        body.extend(event.get("body", b""))
                        if len(body) > 65536:
                            return await self.reject(send, 413)
                        if not event.get("more_body", False):
                            break
            except TimeoutError:
                return await self.reject(send, 408)
            consumed = False
            async def bounded_receive():
                nonlocal consumed
                if not consumed:
                    consumed = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()
            await self.app(scope, bounded_receive, send)
        finally:
            self.active -= 1
