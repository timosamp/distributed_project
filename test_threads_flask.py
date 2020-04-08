from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction
from block import Block
from node import Node
from flask import Flask, jsonify, request
import requests
import flask
from flask_cors import CORS

import json
import jsonpickle
from json import JSONEncoder

import threading
import time

# from rest import app

app = Flask(__name__)
CORS(app)


class apiThread(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name

    def run(self):
        print("Starting " + self.name)
        # Get lock to synchronize threads
        # threadLock.acquire()

        # Register our self
        app.run(host='127.0.0.1', port=5000)

        # Free lock to release next thread
        # threadLock.release()


# create a node
node = Node(0)

# Take its blockchain
blockchain = node.blockchain

node.wallet.balance(blockchain)

# Init lock
threadLock = threading.Lock()

# Init thread
flask_thread = apiThread(1, "Thread-1")

# Start api thread
flask_thread.start()

# Run app request
response = requests.get("http://127.0.0.1/register_node")

# Wait for thread to end
flask_thread.join()

# node.wallet.update_utxos(blockchain.last_block)
