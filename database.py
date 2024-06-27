import asyncpg
import asyncio
from passwords import PASSWORD


class DataBase:
    def __init__(self, host, port, user, dbname, password):
        self.user = user
        self.port = port
        self.dbname = dbname
        self.host = host
        self.password = password
        self.con = None

    async def async_connect(self):
        self.con = await asyncpg.connect(host=self.host,
                                         port=self.port,
                                         database=self.dbname,
                                         password=self.password,
                                         user=self.user)
        await self.con.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                    user_id int PRIMARY KEY,
                    securities TEXT ARRAY
                 )''')
        # TODO create table for securities

    async def user_info(self, user_id: str):
        self.con.fetch('''
        
        ''')


async def main():
    db = DataBase("localhost", 5432, "postgres", "postgres", PASSWORD)
    await db.async_connect()
    await db.user_info("dfs")

asyncio.run(main())
