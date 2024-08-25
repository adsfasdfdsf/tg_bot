import json

import httpx


class API:
    def __init__(self):
        self._client = httpx.AsyncClient()

    async def get_share_by_name(self, security_name: str) -> list:
        params = {"q": security_name, "iss.meta": "off", "securities.columns": "secid,isin,shortname,name,type"}
        response = await self._client.get(url="https://iss.moex.com/iss/securities.json", params=params)
        r = json.loads(await response.aread())
        res = [i for i in r["securities"]["data"] if "share" in i[4]]
        return res

    async def get_bond_by_name(self, security_name: str) -> list:
        params = {"q": security_name, "iss.meta": "off", "securities.columns": "secid,isin,shortname,name,type"}
        response = await self._client.get(url="https://iss.moex.com/iss/securities.json", params=params)
        r = json.loads(await response.aread())
        res = [i for i in r["securities"]["data"] if "bond" in i[4]]
        return res

    async def get_today_security_info(self, security_tiker: str) -> list:
        params = {"tradingsession": '3', 'securities': security_tiker, "iss.meta": "off"}
        response = await self._client.get(url="https://iss.moex.com/iss/engines/stock/markets/shares/secstats.json",
                                          params=params)
        r = json.loads(await response.aread())
        print(r)
        return r[0]["data"]

    async def get_dividends(self, secid: str) -> list:
        params = {"iss.meta": "off", "dividends.columns": "secid,registryclosedate,value,currencyid"}
        response = await self._client.get(url=f"http://iss.moex.com/iss/securities/{secid}/dividends.json",
                                          params=params)
        r = json.loads(await response.aread())
        return r["dividends"]["data"]

    async def get_bondization(self, secid: str) -> list:
        params = {"iss.meta": "off", "coupons.columns": "isin,coupondate,value,faceunit,valueprc"}
        response = await self._client.get(url=f"http://iss.moex.com/iss/securities/{secid}/bondization.json",
                                          params=params)
        r = json.loads(await response.aread())
        return r["coupons"]["data"]

    async def get_bond_history(self, secid: str, from_date, till_date) -> dict:
        params = {"iss.meta": "off", "history.columns": "TRADEDATE,OPEN,CLOSE,HIGH,LOW,CURRENCYID",
                  "from": from_date, "till": till_date}
        response = await self._client.get(url=f"http://iss.moex.com/iss/history/engines"
                                              f"/stock/markets/bonds/securities/{secid}.json",
                                          params=params)
        r = json.loads(await response.aread())
        return r

    async def get_share_history(self, secid: str, from_date, till_date) -> dict:
        params = {"iss.meta": "off", "from": from_date, "till": till_date,
                  "history.columns": "TRADEDATE,OPEN,CLOSE,HIGH,LOW,CURRENCYID",
                  "boardid": "TQBR", "marketprice_board": "1"}
        response = await self._client.get(url=f"http://iss.moex.com/iss/history/engines"
                                              f"/stock/markets/shares/securities/{secid}.json",
                                          params=params)
        r = json.loads(await response.aread())
        return r


