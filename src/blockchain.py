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

import hashlib
import json
import time
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import time

class Transaction:
    def __init__(self, sender, sender_pub, receiver, amount, signature, timestamp=None):
        self.sender = sender
        self.sender_pub = sender_pub
        self.receiver = receiver
        self.amount = float(amount)
        self.signature = signature
        if timestamp:
            self.timestamp = float(timestamp)
        else:
            self.timestamp = time.time()

    def __repr__(self):
        return f"Transaction : [SENDER:{self.sender}, SENDER_PUBLIC_KEY:{self.sender_pub}, RECEIVER:{self.receiver}, AMOUNT:{self.amount}, SIGNATURE:{self.signature}, TIMESTAMP:{self.timestamp}]"
    def to_array(self):
        return [self.sender, self.sender_pub.hex() if isinstance(self.sender_pub, bytes) else self.sender_pub, self.receiver, self.amount, self.signature.hex() if isinstance(self.signature, bytes) else self.signature, self.timestamp]
class Block:
    def __init__(self, index, transaction, previus_hash, timestamp=None):
        if timestamp is None:
            self.timestamp = time.time()
        else:
            self.timestamp = float(timestamp)
        self.index = index
        self.transaction = transaction
        self.previus_hash = previus_hash
        self.hash = self.calculate_hash()
    def calculate_hash(self):
        """
        Calculate the SHA-256 hash of the block's contents.
        """
        block_string = json.dumps(self.to_arr()).encode()
        return hashlib.sha256(block_string).hexdigest()
    def to_array(self):
        return [self.index, self.transaction.to_array(), self.previus_hash, self.hash, self.timestamp]
    def to_arr(self):
        return [self.index, self.transaction.to_array(), self.previus_hash, self.timestamp]
def create_transaction(sender, sender_pub, receiver, amount, private_key_bytes):
    """
    Create a new transaction and sign it with the sender's private key.
    """

    # Create the transaction object
    tx = Transaction(sender, sender_pub, receiver, amount, '')

    # Sign the transaction
    signature = sign_transaction(private_key_bytes, tx.to_array())
    tx.signature = signature

    return tx
def verify_signature(sender_pub, tx: Transaction) -> bool:
    """
    Verify the signature of a transaction using the sender's public key.
    """
    # Create a SHA-256 hash of the transaction data
    tx_data = json.dumps(tx.to_array()).encode('utf-8')
    tx_hash = SHA256.new(tx_data)

    # Load the sender's public key
    public_key = RSA.import_key(sender_pub)

    # Verify the signature
    try:
        pkcs1_15.new(public_key).verify(tx_hash, bytes.fromhex(tx.signature))
        return True
    except (ValueError, TypeError):
        return False

class BlockChain:
    def __init__(self):
        self.chain = []
        self.index = 0
    def create_block(self, previous_hash, transaction, timestamp):
        """
        Create a new block and add it to the chain.
        """
        block = Block(len(self.chain) + 1, transaction, previous_hash, timestamp)
        self.chain.append(block)
        self.index += 1
        return block
    def to_array(self):
        return [block.to_array() for block in self.chain]
    def add_block(self, block):
        """
        Add a block to the chain.
        """
        if len(self.chain) == 0:
            self.chain.append(block)
        else:
            last_block = self.chain[-1]
            if block.previus_hash == last_block.hash:
                self.chain.append(block)
            else:
                raise ValueError("Invalid previous hash")
    def reset(self):
        self.index = 0
        self.chain = []
def generate_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def sign_transaction(private_key_bytes, tx_data):
    key = RSA.import_key(private_key_bytes)
    tx_hash = SHA256.new(json.dumps(tx_data, sort_keys=True).encode('utf-8'))
    signature = pkcs1_15.new(key).sign(tx_hash)
    return signature.hex()
def hash_some(string):
    """
    Hash a string using SHA-256.
    """
    return hashlib.sha256(string.encode()).hexdigest()