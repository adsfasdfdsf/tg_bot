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

    async def get_bond_history(self, secid: str, from_date, till_date):
        params = {"iss.meta": "off", "history.columns": "TRADEDATE,WAPRICE,CURRENCYID",
                  "boardid": "TQBR", "from": from_date, "till": till_date}
        response = await self._client.get(url=f"http://iss.moex.com/iss/history/engines"
                                              f"/stock/markets/bonds/securities/{secid}.json",
                                          params=params)
        r = json.loads(await response.aread())
        return r

    async def get_share_history(self, secid: str, from_date, till_date):
        params = {"iss.meta": "off", "from": from_date, "till": till_date,
                  "history.columns": "TRADEDATE,OPEN,CLOSE,HIGH,LOW,CURRENCYID",
                  "boardid": "TQBR", "marketprice_board": "1"}
        response = await self._client.get(url=f"http://iss.moex.com/iss/history/engines"
                                              f"/stock/markets/shares/securities/{secid}.json",
                                          params=params)
        r = json.loads(await response.aread())
        return r


async def main():
    api = API()
    await api.Init()
    await api.get_share_history("GAZP", "2024-01-01", "2024-07-01")
asyncio.run(main())