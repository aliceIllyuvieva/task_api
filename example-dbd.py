from sqlalchemy import Column, String, Integer, Float, create_engine, null
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy

db_string = ""

base = declarative_base()
db = create_engine(db_string)
base.metadata.create_all(db)


def connect():
    #подключиться к бд
    base.metadata.create_all(db)
    Session = sessionmaker(db)
    session = Session()
    return session


def end_connection(session):
    #отключиться от бд
    session.close()
    db.dispose()


class User(base):
    """
        Класс "Пользователь"
    """
    __tablename__ = 'users'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, default=sqlalchemy.sql.null())
    age = Column(Integer, default=0)
    balance = Column(Integer, default=0)


    def __init__(self, kwargs):
        self.name = kwargs.get('name', '')
        self.age = kwargs.get('age', '')
        self.balance = kwargs.get('balance', '')


    def get_id(self):
        return self.id

    def get_balance(self):
        return self.balance



class BalancesInfo(base):
    """
    Класс "Клиент"
    """
    __tablename__ = 'balances_info'
    user_id = Column(String, default=sqlalchemy.sql.null())
    balance = Column(Integer, default=0)
    date = Column(String, default=sqlalchemy.sql.null())



class TransactionsAll(base):
    """
    Класс "транзакции"
    """
    __tablename__ = 'transactions_all'
    id = Column(Integer, autoincrement=True, primary_key=True)
    type_ = Column(String, default=sqlalchemy.sql.null())
    amount = Column(Integer, default=0)
    person_id = Column(Integer, default=0))



def get_user_balance(idt: int, session):
    #получение баланса юзера через его id
    user = session.query(User).filter_by(id=idt).first()
    if user is None:
        return 0
    else:
        return user.balance


def add_user(name: str, age: int, balance: int, session):
    #добавляет нового юзера в базу
    log = Client(name=name, age=age, balance=balance)
    session.add(log)
    session.commit()


def update_user_balance(user_id, operation, amount, session):
    #перезаписывает баланс юзера, например сразу после того как совершили транзакцию
    query = session.query(User).filter_by(
        id=user_id).first()
    if query is None:
        return 0
    else:
        if operation == '+':
            query.balance += amount
        else:
            query.balance -= amount
        session.commit()
        return 1


base.metadata.create_all(db)
