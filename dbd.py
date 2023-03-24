import sqlalchemy as db
import pandas as pd

config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'user',
    'password': 'password',
    'database': 'testdatabase'
}
db_user = config.get('user')
db_pwd = config.get('password')
db_host = config.get('host')
db_port = config.get('port')
db_name = config.get('database')

connection_str = f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'

#in order to provide some results I fill in the table with potential values, this part can be eliminated in real life untill get_connection() fucn
engine = db.create_engine(connection_str)
connection = engine.connect()
connection.execute("""delete from Users""")
connection.execute("""delete from BalancesInfo""")
connection.execute("""delete from TransactionsAll""")

connection.execute("""INSERT INTO Users (id, name, age, balance) VALUES (1, 'Alice', 25, 2000)""")
connection.execute("""INSERT INTO Users (id, name, age, balance) VALUES (2, 'Bob', 30, 3000)""")
connection.execute("""INSERT INTO Users (id, name, age, balance) VALUES (3, 'Charlie', 35, 4000)""")

connection.execute("""INSERT INTO BalancesInfo (user_id, balance, date) VALUES (1, 2000, '2023-03-22')""")
connection.execute("""INSERT INTO BalancesInfo (user_id, balance, date) VALUES (2, 3000, '2023-03-22')""")
connection.execute("""INSERT INTO BalancesInfo (user_id, balance, date) VALUES (3, 4000, '2023-03-22')""")


def get_connection():
    engine = db.create_engine(connection_str)
    return engine
