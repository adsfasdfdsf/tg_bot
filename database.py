import asyncpg
import asyncio

<<<<<<< HEAD
=======

>>>>>>> origin/db-develop
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
<<<<<<< HEAD

    async def user_info(self, username: str):
        await self.con.execute('''CREATE TABLE IF NOT EXISTS users
         (
            user_id int PRIMARY KEY,
            securities TEXT ARRAY
         )''')

async def main():
    db = DataBase("localhost", 5432, "postgres", "postgres", "18Jul2007")
    await db.async_connect()
    await db.user_info("dfs")

asyncio.run(main())
=======
        await self.con.execute('''CREATE TABLE IF NOT EXISTS users
                         (
                            user_id INT PRIMARY KEY,
                            securities TEXT ARRAY
                         )''')
        await self.con.execute('''CREATE TABLE IF NOT EXISTS securities
                         (
                            security_ticker TEXT PRIMARY KEY,
                            security_fullname TEXT,
                            security_type TEXT
                         )''')
        # TODO create table for securities if needed

    async def get_user_securities(self, user_id):
        res = await self.con.fetch('''
            SELECT *
            FROM users
            WHERE $1 = user_id
            ''', int(user_id))
        if not res:
            return []
        r = res[0]["securities"]
        return r

    async def add_security_to_user(self, user_id, ticker):
        res = await self.con.fetch('''
        SELECT *
        FROM users
        WHERE $1 = user_id
        ''', user_id)
        if not res:
            await self.con.execute(f'''
            INSERT INTO users
            VALUES
            ({user_id}, ARRAY['{ticker.upper()}'])
            ''')
        else:
            await self.con.execute('''
            UPDATE users
            SET securities = array_append(securities, $1)
            WHERE user_id = $2
            ''', ticker.upper(), user_id)

    async def remove_security_from_user(self, user_id, ticker):
        securities = await self.get_user_securities(user_id)
        if ticker.upper() in securities:
            await self.con.execute(f'''
            UPDATE users
            SET securities = array_remove(securities, '{ticker.upper()}')
            WHERE user_id = {int(user_id)}
            ''')

    async def find_security(self, ticker):
        res = self.con.fetch(f'''
        SELECT * 
        FROM securities
        WHERE security_ticker = '{ticker}'
        ''')
        if not res[0]:
            res = self.con.fetch(f'''
                    SELECT * 
                    FROM securities
                    WHERE security_fullname = '{ticker}'
                    ''')
        return res[0]

    async def add_security(self, ticker, fullname, type):
        await self.con.execute(f'''
        INSERT INTO securities
        VALUES
        ('{ticker}', '{fullname}', '{type}')
        ''')
>>>>>>> origin/db-develop
