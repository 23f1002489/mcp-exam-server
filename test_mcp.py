
import asyncio
import hashlib
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

EMAIL = "23f1002489@ds.study.iitm.ac.in"
URL = os.environ.get(
    "MCP_URL",
    "http://127.0.0.1:8000/mcp"
)

async def main():
    for i in range(5):
        challenge = os.urandom(16).hex()

        headers = {
            "X-Exam-Challenge": challenge,
            "X-Exam-Timestamp": "0",
            "X-Exam-Signature": "test"
        }

        async with streamable_http_client(
            URL, headers=headers
        ) as (read, write, _):

            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await session.list_tools()
                assert len(tools.tools) == 1
                assert tools.tools[0].name == "solve_challenge"

                result = await session.call_tool(
                    "solve_challenge",
                    arguments={}
                )

                expected = hashlib.sha256(
                    f"{challenge}:{EMAIL}".encode()
                ).hexdigest()[:16]

                actual = result.content[0].text

                assert not result.isError
                assert len(result.content) == 1
                assert actual == expected

                print(f"Test {i + 1}: PASS")

asyncio.run(main())
