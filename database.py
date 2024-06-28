import asyncpg
import asyncio


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
                    user_id INT PRIMARY KEY,
                    securities TEXT ARRAY
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

    async def add_security(self, user_id, ticker):
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

    async def remove_security(self, user_id, ticker):
        securities = await self.get_user_securities(user_id)
        if ticker.upper() in securities:
            await self.con.execute(f'''
            UPDATE users
            SET securities = array_remove(securities, '{ticker.upper()}')
            WHERE user_id = {int(user_id)}
            ''')

