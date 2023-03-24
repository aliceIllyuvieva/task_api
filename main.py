from flask import Flask, request, jsonify
from datetime import datetime
import dbd
import json
import pandas as pd

app = Flask(__name__)

# Функция добавления пользователя
@app.route('/users', methods=['POST'])
def add_user():
    # Получаем данные пользователя из запроса
    input_1 = request.form.get('user', '')
    input_2 = request.form.get('age', '')
    input_3 = request.form.get('balance', '')

    engine = dbd.get_connection()
    users = pd.read_sql(f"""select * from Users""", engine)
    # Генерируем уникальный идентификатор для пользователя
    user_id = len(users) + 1

    balance_info = pd.read_sql(f"""select * from BalancesInfo""", engine)
    engine.execute(f"""INSERT INTO BalancesInfo (user_id, balance, date) VALUES ({user_id}, {input_3}, '{datetime.today().strftime('%Y-%m-%d')}')""")

    # # Добавляем пользователя в базу данных
    engine.execute(f"""INSERT INTO Users (id, name, age, balance) VALUES ({user_id}, '{input_1}', {input_2}, {input_3})""")


    new_user = pd.read_sql(f"""select * from Users where name = '{input_1}' """, engine)
    user = {}
    user['name'] = str(new_user['name'][0])
    user['age'] = str(new_user['age'][0])
    user['balance'] = str(new_user['balance'][0])
    user['id'] = str(new_user['id'][0])
    # Возвращаем ответ с информацией о новом пользователе
    return jsonify(user), 201


# Функция просмотра текущих пользователей
@app.route('/users', methods=['GET'])
def get_users():
    engine = dbd.get_connection()
    users = pd.read_sql(f"""select * from Users""", engine)
    users = users.to_json('t.json',orient='records', indent=4)
    with open("t.json") as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    # Возвращаем ответ с информацией о пользователях
    return jsonify(jsonObject), 201


# Функция добавления транзакции
@app.route('/transactions', methods=['POST'])
def add_transaction():
    engine = dbd.get_connection()
    # Получаем данные транзакции из запроса
    transaction_type = request.form.get('transaction_type', '')
    user_id = int(request.form.get('user_id', ''))
    amount = float(request.form.get('amount', ''))
    
    # Проверяем, что пользователь с таким идентификатором существует
    user = pd.read_sql(f"""select * from Users where id = {user_id}""", engine)

    if user.empty:
        return jsonify({'error': 'User not found'}), 404
    
    # Проверяем, что тип транзакции указан корректно
    if transaction_type not in ['DEPOSIT', 'WITHDRAW']:
        return jsonify({'error': 'Invalid transaction type'}), 400
    
    # Проверяем, что сумма транзакции положительна
    if amount <= 0:
        return jsonify({'error': 'Transaction amount must be positive'}), 400

    # Обновляем баланс пользователя в зависимости от типа транзакции
    transactions_all = pd.read_sql(f"""select * from TransactionsAll""", engine)
    trans_id = len(transactions_all) + 1
    if transaction_type == 'DEPOSIT':

        new_b = user['balance'][0] + amount
        engine.execute(f"""UPDATE Users SET balance = {new_b} where id = {user['id'][0]}""")
        engine.execute(f"""INSERT INTO TransactionsAll (type, amount, person_id, id) VALUES ('DEPOSIT', {amount}, {user_id}, {trans_id})""")

    else:
        if user['balance'][0] < amount:
            return jsonify({'error': 'Not enough balance'}), 400
        else:
            new_b = user['balance'][0] - amount
            engine.execute(f"""UPDATE Users SET balance = {new_b} where id = {user['id'][0]}""")
            engine.execute(f"""INSERT INTO TransactionsAll (type, amount, person_id, id) VALUES ('WITHDRAW', {amount}, {user_id}, {trans_id})""")

    transactions = pd.read_sql(f"""select * from TransactionsAll""", engine)
    transactions = transactions.to_json('t.json',orient='records', indent=4)
    with open("t.json") as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    return jsonify(jsonObject), 201


# Функция просмотра всех транзакций
@app.route('/transactions', methods=['GET'])
def get_transactions():
    engine = dbd.get_connection()
    transactions_all = pd.read_sql(f"""select * from TransactionsAll""", engine)
    transactions_all = transactions_all.to_json('t.json',orient='records', indent=4)
    with open("t.json") as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    # Возвращаем ответ с информацией о всех транзакциях
    return jsonify(jsonObject), 201


# Функция просмотра конкретной транзакции
@app.route('/transactions_info/<id_transaction>', methods=['GET'])
def get_transactions_by_person(id_transaction:int):
    engine = dbd.get_connection()
    transaction = pd.read_sql(f"""select * from TransactionsAll where id = {id_transaction}""", engine)
    if transaction.empty == False:
        t = {}
        t['type'] = str(transaction['type'][0])
        t['amount'] = str(transaction['amount'][0])
        t['person_id'] = str(transaction['person_id'][0])
        t['id'] = str(transaction['id'][0])
        return jsonify(t), 201
    else:
        return jsonify({'error': 'No such transaction'}), 400


# Функция просмотра текущего баланса пользователя
@app.route('/user/<idt>/balance', methods=['GET'])
def get_user_balance(idt: int):
    engine = dbd.get_connection()
    user_balance = pd.read_sql(f"""select * from Users where id = {idt}""", engine)
    if user_balance.empty == False:
        u = {}
        u['user_id'] = str(user_balance['id'][0])
        u['balance'] = str(user_balance['name'][0])
        u['date'] = str(user_balance['age'][0])
        u['balance'] = str(user_balance['balance'][0])
        return jsonify(u), 201
    else:
        return jsonify({'error': 'No such user'}), 400


# Функция обновления инфо по балансу юзера (запускаем например в конце дня один раз)
@app.route('/balance/info/update', methods=['POST'])
def update_balance():
    engine = dbd.get_connection()
    users = pd.read_sql(f"""select id from Users""", engine)
    users = set(users['id'])
    for user in users:
        balance = pd.read_sql(f"""select balance from Users where id = {user}""", engine)
        engine.execute(f"""INSERT INTO BalancesInfo (user_id, balance, date) VALUES ({user}, {float(balance['balance'][0])}, '{datetime.today().strftime('%Y-%m-%d')}') """)

    # Возвращаем ответ с информацией о балансах по датам
    balances = pd.read_sql(f"""select * from BalancesInfo""", engine)
    balances.to_json('t.json',orient='records', indent=4)
    with open("t.json") as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    return jsonify(jsonObject), 201


# Функция получения инфо о балансах
@app.route('/balance/db', methods=['GET'])
def get_balance_db():
    engine = dbd.get_connection()
    balances = pd.read_sql(f"""select * from BalancesInfo""", engine)
    balances.to_json('t.json',orient='records', indent=4)
    with open("t.json") as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    # Возвращаем ответ с информацией о балансах по датам
    return jsonify(jsonObject), 201


# Функция получения инфо о балансе человека на конкретную дату
@app.route('/user/<idt>/balance/by/date', methods=['GET'])
def get_user_balance_by_date(idt):
    engine = dbd.get_connection()
    input_date = request.form.get('date', '')
    balances = pd.read_sql(f"""select * from BalancesInfo where user_id = {idt} and date = '{input_date}' """, engine)
    if balances.empty == False:
        balances.to_json('t.json',orient='records', indent=4)
        with open("t.json") as jsonFile:
            jsonObject = json.load(jsonFile)
            jsonFile.close()
            return jsonify(jsonObject), 201
    else:
        return jsonify({'error': 'No such user or no such date in db'}), 400


# Запускаем сервер
if __name__ == '__main__':
    app.run(debug=True)
