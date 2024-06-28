import httpx
from httpx import Response, Request, AsyncClient
import asyncio
import json


class API:
    def __init__(self):
        self._client = None

    async def Init(self):
        self._client = httpx.AsyncClient()

    async def get_security_by_name(self, security_name: str):
        params = {"q": security_name, "iss.meta": "off", "securities.columns": "secid,isin,shortname,name,type"}
        response = await self._client.get(url="https://iss.moex.com/iss/securities.json", params=params)
        r = json.loads(await response.aread())
        print(r)
        res = r["securities"]["data"]
        return res

    async def get_today_security_info(self, security_tiker: str):
        params = {'securities': security_tiker, "iss.meta": "off", "secstats.column": ""}
        response = await self._client.get(url="https://iss.moex.com/iss/engines/stock/markets/shares/secstats.json",
                                          params=params)
        r = json.loads(await response.aread())
        print(r)

    async def get_dividends(self, secid: str):
        params = {"iss.meta": "off"}
        response = await self._client.get(url=f"http://iss.moex.com/iss/securities/{secid}/dividends.json",
                                          params=params)
        r = json.loads(await response.aread())
        print(r)

    async def get_bondization(self, secid: str):
        params = {"iss.meta": "off"}
        response = await self._client.get(url=f"http://iss.moex.com/iss/securities/{secid}/bondization.json",
                                          params=params)
        r = json.loads(await response.aread())
        print(r)


