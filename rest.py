import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

import time

from blockchain import Blockchain
from block import Block
import block
import node
import wallet
import transaction
import wallet

### JUST A BASIC EXAMPLE OF A REST API WITH FLASK


app = Flask(__name__)
CORS(app)
blockchain = Blockchain()


# .......................................................................................


# get all transactions in the blockchain

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200


# Flask's way of declaring end-points

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201


# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
