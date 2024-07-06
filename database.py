import asyncpg


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
        await self.con.execute('''CREATE TABLE IF NOT EXISTS securities
                         (
                            secid TEXT PRIMARY KEY,
                            isin TEXT,
                            shortname TEXT,
                            name TEXT,
                            type TEXT
                         )''')

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
            if ticker.upper() not in res[0]["securities"]:
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
        res = await self.con.fetch(f'''
        SELECT * 
        FROM securities
        WHERE secid = '{ticker.upper()}'
        ''')
        return res[:]

    async def add_security(self, secid, isin, shortname, name, type):
        await self.con.execute(f'''
        INSERT INTO securities
        VALUES
        ('{secid.upper()}', '{isin.upper()}', '{shortname}', '{name}', '{type}')
        ''')

