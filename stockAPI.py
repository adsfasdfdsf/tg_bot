import httpx
from httpx import Response, Request, AsyncClient
import asyncio
import json


class API:
    def __init__(self, client):
        self._client = client

    async def get_security_by_name(self, security_name: str):
        params = {"q": security_name, "iss.meta": "off"}
        response = await self._client.get(url="https://iss.moex.com/iss/securities.json", params=params)
        r = json.loads(await response.aread())
        result_list = list()
        if "securities" in r:
            columns = r["columns"]


async def main():
    async with httpx.AsyncClient() as ascl:
        app = API(ascl)
        await app.get_json_info("Apple")


asyncio.run(main())