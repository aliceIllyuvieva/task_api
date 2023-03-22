from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Пример базы данных пользователей
users = [
    {"id": 1, "name": "Alice", "age": 25, "balance": 2000},
    {"id": 2, "name": "Bob", "age": 30, "balance": 3000},
    {"id": 3, "name": "Charlie", "age": 35, "balance": 4000},
]

balances_info = [{"user_id": 1, "balance": 2000, "date": '2023-03-22'},
                {"user_id": 2,  "balance": 3000, "date": '2023-03-22'},
                {"user_id": 3,  "balance": 4000, "date": '2023-03-22'},
]

transactions_all = []

# Функция добавления пользователя
@app.route('/users', methods=['POST'])
def add_user():
    # Получаем данные пользователя из запроса
    input_1 = request.form.get('user', '')
    input_2 = request.form.get('age', '')
    input_3 = request.form.get('balance', '')
    
    # # Генерируем уникальный идентификатор для пользователя
    user_id = len(users) + 1

    user = {}
    user['name'] = input_1
    user['age'] = input_2
    user['balance'] = int(input_3)
    user['id'] = user_id

    balance_info = {}
    balance_info['user_id'] = user_id
    balance_info['balance'] = int(input_3)
    balance_info['date'] = datetime.today().strftime('%Y-%m-%d')
    balances_info.append(balance_info)
    # # Добавляем пользователя в базу данных
    users.append(user)

    # Возвращаем ответ с информацией о новом пользователе
    return jsonify(user), 201


# Функция просмотра текущих пользователей
@app.route('/users', methods=['GET'])
def get_users():

    # Возвращаем ответ с информацией о пользователях
    return jsonify(users), 201


# Функция добавления транзакции
@app.route('/transactions', methods=['POST'])
def add_transaction():
    # Получаем данные транзакции из запроса
    transaction_type = request.form.get('transaction_type', '')
    user_id = int(request.form.get('user_id', ''))
    amount = float(request.form.get('amount', ''))
    # transaction_type = transaction.get('type')
    
    # Проверяем, что пользователь с таким идентификатором существует
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Проверяем, что тип транзакции указан корректно
    if transaction_type not in ['DEPOSIT', 'WITHDRAW']:
        return jsonify({'error': 'Invalid transaction type'}), 400
    
    # Проверяем, что сумма транзакции положительна
    if amount <= 0:
        return jsonify({'error': 'Transaction amount must be positive'}), 400
    transactions = {}
    # Обновляем баланс пользователя в зависимости от типа транзакции
    trans_id = len(transactions_all) + 1
    if transaction_type == 'DEPOSIT':
        user['balance'] += amount
        transactions['type'] = 'DEPOSIT'
        transactions['amount'] = amount
        transactions['person_id'] = user_id
        transactions['id'] = trans_id
        transactions_all.append(transactions)
    else:
        if user['balance'] < amount:
            return jsonify({'error': 'Not enough balance'}), 400
        else:
            user['balance'] -= amount
            transactions['type'] = 'WITHDRAW'
            transactions['amount'] = amount
            transactions['person_id'] = user_id
            transactions['id'] = trans_id
            transactions_all.append(transactions)
    return jsonify(transactions), 201


# Функция просмотра всех транзакций
@app.route('/transactions', methods=['GET'])
def get_transactions():

    # Возвращаем ответ с информацией о всех транзакциях
    return jsonify(transactions_all), 201


# Функция просмотра конкретной транзакции
@app.route('/transactions_info/<id_transaction>', methods=['GET'])
def get_transactions_by_person(id_transaction:int):
    tr = ''
    existence = 0
    for t in transactions_all:
        if int(t['id']) == int(id_transaction):
            # Возвращаем ответ с информацией о транзакции
            existence = 1
            return jsonify(t), 201
    if existence == 0:
        return jsonify({'error': 'No such transaction'}), 400


# Функция просмотра текущего баланса пользователя
@app.route('/user/<idt>/balance', methods=['GET'])
def get_user_balance(idt: int):
    existence = 0
    for user in users:
        if int(user['id']) == int(idt):
            # Возвращаем ответ с информацией о балансе пользователя
            existence = 1
            return jsonify(user), 201
    if existence == 0:
        return jsonify({'error': 'No such user'}), 400


# Функция обновления инфо по балансу юзера (запускаем например в конце дня один раз)
@app.route('/balance/info/update', methods=['POST'])
def update_balance():
    for user in users:
        balance_i = {}
        balance_i['user_id'] = user['id']
        balance_i['balance'] = user['balance']
        balance_i['date'] = datetime.today().strftime('%Y-%m-%d')
        balances_info.append(balance_i)

    # Возвращаем ответ с информацией о балансах по датам
    return jsonify(balances_info), 201


@app.route('/balance/db', methods=['GET'])
def get_balance_db():

    # Возвращаем ответ с информацией о балансах по датам
    return jsonify(balances_info), 201


# Функция обновления инфо по балансу юзера (запускаем например в конце дня один раз)
@app.route('/user/<idt>/balance/by/date', methods=['GET'])
def get_user_balance_by_date(idt):
    existence = 0
    input_date = request.form.get('date', '')
    for row in balances_info:
        if int(row['user_id']) == int(idt) and str(row['date']) == str(input_date):
            # Возвращаем ответ с информацией о балансе юзера на конкретную дату

            return jsonify(row), 201
    if existence == 0:
        return jsonify({'error': 'No such user or no such date in db'}), 400


# Запускаем сервер
if __name__ == '__main__':
    app.run(debug=True)