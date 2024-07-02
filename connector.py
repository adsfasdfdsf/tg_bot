from database import DataBase
from passwords import DBNAME, PASSWORD, PORT, USER, HOST
from stockAPI import API
from graphics import draw_price_graph
import time
import asyncio

class Connector:
    def __init__(self):
        self.database = DataBase(dbname=DBNAME, user=USER, host=HOST, password=PASSWORD, port=PORT)
        self.api = API()

    async def Init(self):
        await self.database.async_connect()
        await self.api.Init()

    async def get_user_securities(self, user_id):
        return await self.database.get_user_securities(user_id)

    async def find_security(self, ticker):
        res = await self.database.find_security(ticker)
        if res:
            print(res)
            return res
        response = await self.api.get_security_by_name(ticker)
        print(response)
        if not response:
            print(1)
            return []
        result = []
        for i in response:
            if i[0] == ticker.upper():
                result.clear()
                a = {}
                a["secid"] = i[0]
                a["isin"] = i[1]
                a["shortname"] = i[2]
                a["name"] = i[3]
                a["type"] = i[4]
                print(a)
                result.append(a)
                return result
            a = {}
            a["secid"] = i[0]
            a["isin"] = i[1]
            a["shortname"] = i[2]
            a["name"] = i[3]
            a["type"] = i[4]
            print(a)
            result.append(a)

        print(result)
        return result

    async def add_security_to_db(self, secid, isin, shortname, name, type):
        if not await self.database.find_security(secid):
            await self.database.add_security(secid, isin, shortname, name, type)

    async def add_security(self, user_id, ticker):
        await self.database.add_security_to_user(user_id, ticker)

    async def remove_security(self, user_id, ticker):
        await self.database.remove_security_from_user(user_id, ticker)

    async def draw_price_graphic(self, secid):
        sec = await self.database.find_security(secid)
        if len(sec) == 0:
            return "Error"
        data = []
        if sec[0]["type"].count("share") > 0:
            data = await self.api.get_share_history(secid, "2021-01-01", time.strftime("%Y-%m-%d"))
        elif sec[0]["type"].count("bond") > 0:
            data = await self.api.get_bond_history(secid, "2021-01-01", time.strftime("%Y-%m-%d"))
        draw_price_graph(sec[0]["shortname"], data["history"]["data"])


async def main():
    con = Connector()
    await con.Init()
    await con.draw_price_graphic("GAZP")
asyncio.run(main())