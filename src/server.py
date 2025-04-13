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

from flask import Flask, request, jsonify, render_template, redirect, url_for
from blockchain import BlockChain, Transaction, verify_signature, Block
import json
import os

app = Flask(__name__)
DATA_FILE = "chain.json"
if os.pathe.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    chain = BlockChain()
    for block in data:
        tx = Transaction(**block[1])
        index = block[0]
        previus_hash = block[2]
        hash = block[3]
        timestamp = block[4]
        block = Block(index, tx, previus_hash)
        block.hash = hash
        block.timestamp = timestamp
        chain.add_block(block)
else:
    chain = BlockChain()
def save_chain():
    with open(DATA_FILE, "w") as f:
        json.dump(chain.to_array(), f)
@app.route("/send", methods=["POST"])
def send_transaction():
    data = request.get_json()
    sender = data["sender"]
    receiver = data["receiver"]
    amount = data["amount"]
    private_key_bytes = data["private_key_bytes"]
    # Create a new transaction
    tx = chain.create_transaction(sender, receiver, amount, private_key_bytes)
    # Add the transaction to the blockchain
    chain.add_transaction(tx)
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
    balance = 0
    for block in chain.chain:
        tx = block.transaction
        if tx.sender == user:
            balance -= tx.amount
        elif tx.receiver == user:
            balance += tx.amount
    return jsonify({"balance": balance})
if __name__=="__main__":
    app.run(port=5000, debug=True)