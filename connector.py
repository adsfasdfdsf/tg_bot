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

    async def add_security(self, user_id, ticker):
        await self.database.add_security(user_id, ticker)

    async def remove_security(self, user_id, ticker):
        await self.database.remove_security(user_id, ticker)
