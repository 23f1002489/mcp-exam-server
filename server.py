
import hashlib
import os
from contextvars import ContextVar

from mcp.server.fastmcp import FastMCP
import uvicorn

EMAIL = "23f1002489@ds.study.iitm.ac.in".strip().lower()

challenge_context = ContextVar(
    "exam_challenge", default=None
)

mcp = FastMCP(
    "Exam Challenge Server",
    stateless_http=True,
    json_response=True,
    streamable_http_path="/mcp",
)


@mcp.tool()
def solve_challenge() -> str:
    """Solve the challenge from the current HTTP headers."""
    challenge = challenge_context.get()

    if challenge is None:
        raise ValueError("Missing X-Exam-Challenge header")

    result = hashlib.sha256(
        f"{challenge}:{EMAIL}".encode("utf-8")
    ).hexdigest()

    return result[:16]


# ASGI middleware to capture each request's headers.
class ChallengeMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {
            key.decode("latin-1").lower():
            value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }

        challenge = headers.get("x-exam-challenge")
        token = challenge_context.set(challenge)

        try:
            await self.app(scope, receive, send)
        finally:
            challenge_context.reset(token)


app = ChallengeMiddleware(mcp.streamable_http_app())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
    )
