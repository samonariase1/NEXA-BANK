from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import random

app = Flask(__name__)
CORS(app)

# Mock database
users_db = {
    "user1": {
        "id": "user1",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "accounts": {
            "main": {
                "balance": 10000000000,  # ₦10 billion
                "currency": "NGN",
                "transactions": []
            }
        },
        "preferences": {
            "dark_mode": False,
            "notifications": True
        }
    }
}

# Helper functions
def generate_transaction_id():
    return f"txn_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"

def log_transaction(user_id, account_id, amount, description, category):
    transaction = {
        "id": generate_transaction_id(),
        "amount": amount,
        "description": description,
        "category": category,
        "date": datetime.datetime.now().isoformat(),
        "status": "completed"
    }
    
    users_db[user_id]["accounts"][account_id]["transactions"].insert(0, transaction)
    users_db[user_id]["accounts"][account_id]["balance"] += amount
    
    return transaction

# API Endpoints
@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    # Remove sensitive data before sending
    user_data = users_db[user_id].copy()
    del user_data["accounts"]
    
    return jsonify(user_data)

@app.route('/api/user/<user_id>/accounts', methods=['GET'])
def get_accounts(user_id):
    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(users_db[user_id]["accounts"])

@app.route('/api/user/<user_id>/transactions', methods=['GET'])
def get_transactions(user_id):
    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    account_id = request.args.get('account', 'main')
    limit = int(request.args.get('limit', 10))
    
    if account_id not in users_db[user_id]["accounts"]:
        return jsonify({"error": "Account not found"}), 404
    
    transactions = users_db[user_id]["accounts"][account_id]["transactions"][:limit]
    return jsonify(transactions)

@app.route('/api/user/<user_id>/transfer', methods=['POST'])
def transfer_funds(user_id):
    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    account_id = data.get('account', 'main')
    recipient = data.get('recipient')
    amount = float(data.get('amount'))
    description = data.get('description', '')
    
    if account_id not in users_db[user_id]["accounts"]:
        return jsonify({"error": "Account not found"}), 404
    
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    
    if users_db[user_id]["accounts"][account_id]["balance"] < amount:
        return jsonify({"error": "Insufficient funds"}), 400
    
    # In a real app, we would validate the recipient and process the transfer
    transaction = log_transaction(
        user_id, account_id, -amount,
        f"Transfer to {recipient[-4:]} - {description}",
        "transfer"
    )
    
    # Simulate recipient receiving funds
    log_transaction(
        "user1", "main", amount,
        f"Transfer from {user_id[:4]}*** - {description}",
        "deposit"
    )
    
    return jsonify({
        "message": "Transfer successful",
        "transaction": transaction,
        "new_balance": users_db[user_id]["accounts"][account_id]["balance"]
    })

@app.route('/api/user/<user_id>/preferences', methods=['GET', 'PUT'])
def user_preferences(user_id):
    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == 'GET':
        return jsonify(users_db[user_id]["preferences"])
    
    if request.method == 'PUT':
        data = request.get_json()
        for key, value in data.items():
            if key in users_db[user_id]["preferences"]:
                users_db[user_id]["preferences"][key] = value
        
        return jsonify({
            "message": "Preferences updated",
            "preferences": users_db[user_id]["preferences"]
        })

# Market Data API
@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    # Simulate real market data
    currencies = {
        "USD_NGN": {
            "rate": random.uniform(1400, 1600),
            "change": random.uniform(-2, 2)
        },
        "EUR_NGN": {
            "rate": random.uniform(1500, 1700),
            "change": random.uniform(-2, 2)
        },
        "GBP_NGN": {
            "rate": random.uniform(1800, 2000),
            "change": random.uniform(-2, 2)
        }
    }
    
    crypto = {
        "BTC": {
            "price": random.uniform(60000, 70000),
            "change": random.uniform(-5, 5)
        },
        "ETH": {
            "price": random.uniform(3000, 4000),
            "change": random.uniform(-5, 5)
        }
    }
    
    return jsonify({
        "currencies": currencies,
        "crypto": crypto,
        "timestamp": datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)