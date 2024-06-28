from database import DataBase
from passwords import DBNAME, PASSWORD, PORT, USER, HOST
from stockAPI import API

#TODO Api requests
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
            return [res]
        response = await self.api.get_security_by_name(ticker)
        if not response:
            return []
        counter = 0
        ind = -1
        for i in response:
            if response[i][0] == ticker:
                counter += 1
                ind = i
        if counter == 1:
            return [response[ind]]
        return response

    async def add_security(self, user_id, ticker):
        await self.database.add_security_to_user(user_id, ticker)

    async def remove_security(self, user_id, ticker):
        await self.database.remove_security_from_user(user_id, ticker)
