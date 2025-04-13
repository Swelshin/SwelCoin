# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Copyright (c) 2025 Guillermo Leira Temes

from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
from blockchain import BlockChain, Transaction, verify_signature, Block, create_transaction, generate_keys
from tinrux import cookies, client, server
import json
import os
import secrets
import threading
import time
import datetime

HOST = "0.0.0.0" # change by your needs
PORT = 6001 # change by your needs
START_BALANCE = 0 # change by your needs

tserver = server.TinruxServer(HOST, PORT)
sbase = threading.Thread(target=tserver.main, daemon=True)
sbase.start()
time.sleep(1) # wait for the server to start
db = client.TinruxClient(HOST, PORT)
cookiem = cookies.TinruxCookies(HOST, PORT)

COOKIE_LIVE = 3600

app = Flask(__name__)
DATA_FILE = "chain.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    chain = BlockChain()
    for block in data:
        tx = Transaction(*block[1])
        index = block[0]
        previus_hash = block[2]
        hash = block[3]
        timestamp = block[4]
        block = Block(index, tx, previus_hash)
        block.hash = hash
        block.timestamp = timestamp
        chain.add_block(block)
    chain.index = len(chain.chain)
else:
    chain = BlockChain()


def gen_cookie():
    """
    Generate a random cookie.
    """
    return secrets.token_hex(32)

def save_chain():
    with open(DATA_FILE, "w") as f:
        json.dump(chain.to_array(), f)
@app.route("/send", methods=["POST"])
def send_transaction():
    data = request.get_json()
    db.send_command("SAVE")
    print(data)
    sender = data["sender"]
    receiver = data["receiver"]
    amount = data["amount"]
    timestamp = data["timestamp"]
    balance = get_balance(sender).json["balance"]
    if balance < float(amount) and sender != "0": # this allows to create the genesis block
        return jsonify({"error": "Insufficient balance"}), 400
    # Generate a new key pair for the sender
    private_key_bytes, sender_pub = generate_keys()
    # Create a new transaction
    tx = create_transaction(sender, sender_pub, receiver, amount, private_key_bytes)
    # Add the transaction to the blockchain
    chain.create_block(chain.chain[-1].hash if chain.chain else "0", tx, timestamp)
    # Save the blockchain to a file
    save_chain()
    return jsonify({"message": "Transaction added", "transaction": tx.to_array()})
@app.route("/chain", methods=["GET"])
def get_chain():
    """
    Get the entire blockchain.
    """
    return jsonify(chain.to_array())
@app.route("/balance/<user>", methods=["GET"])
def get_balance(user):
    """
    Get the balance of a user.
    """
    balance = START_BALANCE
    for block in chain.chain:
        tx = block.transaction
        if tx.sender == user:
            balance -= tx.amount
        elif tx.receiver == user:
            balance += tx.amount
    return jsonify({"balance": balance})

def export_balances():
    """
    Export the balances of all users to a file.
    """
    balances = {}
    for block in chain.chain:
        tx = block.transaction
        if tx.sender not in balances:
            balances[tx.sender] = START_BALANCE
        if tx.receiver not in balances:
            balances[tx.receiver] = START_BALANCE
        if tx.sender != "0":
            balances[tx.sender] -= tx.amount
        if tx.receiver != "0":
            balances[tx.receiver] += tx.amount
    with open("balances.json", "w") as f:
        json.dump(balances, f)

# Web interface
@app.route("/")
def index():
    """
    Render the index page.
    """
    return render_template("index.html", chain=chain.to_array())
@app.route("/register", methods=["POST", "GET"])
def register():
    db.send_command("SAVE")
    """
    Render the registration page.
    """
    if request.method == "POST":
        username = request.form["username"]
        hashed_password = request.form["hashed_password"]
        # Save the user to a database or file
        # For now, just print it to the console
        cookie_value = gen_cookie()
        # Check if the user already exists
        try:
            if db.send_command("GET", str(username)).startswith("ERR"):
                pass
            else:
                return "User already exists", 400
        except Exception as e:
            print(f"Error checking user: {e}")
        print(db.send_command("SET", username, hashed_password))
        cookiem.create_cookie(f"session:{username}", cookie_value, COOKIE_LIVE)
        print(f"User registered: {username}, {hashed_password}")
        response = make_response(redirect(url_for("dashboard")))  # Redirigimos a la página del dashboard
        response.set_cookie('session', cookie_value, max_age=COOKIE_LIVE, httponly=True)
        response.set_cookie('username', username, max_age=COOKIE_LIVE, httponly=True)
        return response
    return render_template("register.html")
@app.route("/dashboard")
def dashboard():
    """
    Renderiza el panel del usuario usando cookies.
    """
    username = request.cookies.get("username")
    session_cookie = request.cookies.get("session")

    # Comprobar si las cookies existen
    if not username or not session_cookie:
        return redirect(url_for("login"))

    # Comprobar si la sesión es válida
    valid_session = cookiem.get_cookie(f"session:{username}")
    if valid_session != session_cookie:
        return "Invalid Session", 401

    # Si la sesión es válida, mostramos la cuenta del usuario
    return render_template("dashboard.html", username=username)
@app.route("/login", methods=["POST", "GET"])
def login():
    """
    Render the login page.
    """
    if request.method == "POST":
        username = request.form["username"]
        hashed_password = request.form["hashed_password"]
        # Check the user against a database or file
        # For now, just print it to the console
        if db.send_command("GET", username) != hashed_password:
            return "Invalid username or password", 401
        cookie_value = gen_cookie()
        cookiem.create_cookie(f"session:{username}", cookie_value, COOKIE_LIVE)
        print(f"User logged in: {username}, {hashed_password}")
        response = make_response(redirect(url_for("dashboard")))  # Redirigimos a la página del dashboard
        response.set_cookie('session', cookie_value, max_age=COOKIE_LIVE, httponly=True)
        response.set_cookie('username', username, max_age=COOKIE_LIVE, httponly=True)
        return response
    return render_template("login.html")

if __name__=="__main__":
    app.run(host=HOST, port=8000, debug=False)
