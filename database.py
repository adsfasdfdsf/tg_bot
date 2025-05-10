import asyncpg


class DataBase:
    def __init__(self, host, port, user, dbname, password):
        self.user = user
        self.port = port
        self.dbname = dbname
        self.host = host
        self.password = password

    async def get_user_securities(self, user_id):
        user_id = str(user_id)
        con = await asyncpg.connect(host=self.host,
                                    port=self.port,
                                    database=self.dbname,
                                    password=self.password,
                                    user=self.user)
        res = await con.fetch('''
            SELECT *
            FROM users
            WHERE $1 = user_id
            ''', user_id)
        await con.close()
        if not res:
            return []
        r = res[0]["securities"]
        return r

    async def add_security_to_user(self, user_id, ticker):
        user_id = str(user_id)
        con = await asyncpg.connect(host=self.host,
                                    port=self.port,
                                    database=self.dbname,
                                    password=self.password,
                                    user=self.user)
        res = await con.fetch('''
        SELECT *
        FROM users
        WHERE $1 = user_id
        ''', user_id)
        if not res:
            await con.execute(f'''
            INSERT INTO users
            VALUES
            ({user_id}, ARRAY['{ticker.upper()}'])
            ''')
        else:
            if ticker.upper() not in res[0]["securities"]:
                await con.execute('''
                UPDATE users
                SET securities = array_append(securities, $1)
                WHERE user_id = $2
                ''', ticker.upper(), user_id)
        await con.close()

    async def remove_security_from_user(self, user_id, ticker):
        user_id = str(user_id)
        con = await asyncpg.connect(host=self.host,
                                    port=self.port,
                                    database=self.dbname,
                                    password=self.password,
                                    user=self.user)
        securities = await self.get_user_securities(user_id)
        if ticker.upper() in securities:
            await con.execute(f'''
            UPDATE users
            SET securities = array_remove(securities, '{ticker.upper()}')
            WHERE user_id = {user_id}
            ''')
        await con.close()

    async def find_security(self, ticker):
        con = await asyncpg.connect(host=self.host,
                                    port=self.port,
                                    database=self.dbname,
                                    password=self.password,
                                    user=self.user)
        res = await con.fetch(f'''
        SELECT * 
        FROM securities
        WHERE secid = '{ticker.upper()}'
        ''')
        await con.close()
        return res[:]

    async def add_security(self, secid, isin, shortname, name, type):
        con = await asyncpg.connect(host=self.host,
                                    port=self.port,
                                    database=self.dbname,
                                    password=self.password,
                                    user=self.user)
        await con.execute(f'''
        INSERT INTO securities
        VALUES
        ('{secid.upper()}', '{isin.upper()}', '{shortname}', '{name}', '{type}')
        ''')
        await con.close()
