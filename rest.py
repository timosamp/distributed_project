# https://github.com/satwikkansal/python_blockchain_app/blob/master/node_server.py
import flask
import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

import time
import datetime
import json

from blockchain import Blockchain
from block import Block
from node import Node
from wallet import Wallet
from transaction import Transaction

from test_threads_flask import node, app

import jsonpickle

# app = Flask(__name__)
# CORS(app)

# .......................................................................................

# # create a node
# node = Node(0)

# Take the blockchain of node (import from client)
blockchain = node.blockchain
# the address to other participating members of the network
peers = node.peers


# get all transactions in the blockchain
@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    list_of_transactions = blockchain.get_transactions()
    response = {'transactions': list_of_transactions}
    return jsonpickle.encode(response), 200
    # return jsonify(response), 200


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["sender_address", "recipient_address", "amount", "timestamp",
                       "transaction_inputs", "transaction_outputs", "signature"]

    # Check if every field has data
    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    incoming_transaction = jsonpickle.decode(tx_data)

    blockchain.add_new_transaction(incoming_transaction)

    print("/new_transaction: ")
    print(incoming_transaction)

    return "Success", 201


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        data_json = jsonpickle.encode(block)

        requests.post(url,
                      data=data_json,
                      headers=headers)


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    required_fields = ["index", "transactions", "timestamp", "previous_hash", "nonce"]

    # Check if every field has data
    for field in required_fields:
        if not block_data.get(field):
            return "Invalid transaction data", 404

    # Decode object from json
    block = jsonpickle.decode(block_data)

    # Verify it
    verified = False

    # If block has the proof of work the continue with more checks.
    # If block doesn't have valid pow, discard it.
    if blockchain.is_valid_proof(block):

        if blockchain.is_block_valid(block):
            # If the rest test succeed then add block into blockchain
            blockchain.add_block(block)

            # Change the flag for the corresponding response
            verified = True

        else:
            # If not, call the consesus algorithm to check
            # if there is longer valid chain available.
            consensus()

    if not verified:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# Endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to register a node
@app.route('/chain', methods=['GET'])
def get_node_data():
    chain_len = len(node.blockchain.chain)
    chain_json = jsonpickle.encode(node.blockchain.chain)

    return json.dumps({"length": chain_len,
                       "chain": chain_json,
                       "peers": node.peers})


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():

    # global node

    # Get node's public key
    public_key = request.get_json()["public_key"]
    if not public_key:
        return "Invalid data", 400

    # Get node's ip address
    ip_address = request.remote_addr

    # Build tuple for peer's list
    node_register_data = (public_key, ip_address)

    # Add it into the peer's list
    node.peers.append(node_register_data)

    # Fixme: check if node has already been registered
    while len(node.peers) < 5:
        time.sleep(0.5)         # wait 0.5 sec

    return get_node_data(), 200


# Get the chain only by hashes.
# This endpoint will be used by our app
# for find the longest chain in consesus algorithm
@app.route('/chain_by_hashes', methods=['GET'])
def get_chain_by_hashes():
    chain_len = len(blockchain.chain)

    chain_hashes = []

    for block in blockchain.chain:
        chain_hashes.append(block.hash)

    chain_hashes_json = jsonpickle.encode(chain_hashes)

    return json.dumps({"length": chain_len,
                       "chain": chain_hashes_json})


@app.route('/get_block_from', methods=['POST'])
def get_blocks_from():
    hash_data = request.get_json()

    # Save first hash of node's fork
    first_fork_hash = jsonpickle.decode(hash_data.get("first_fork_hash"))

    # Init list
    fork_blocks = []

    # Collect fork's block
    for block in reversed(blockchain.chain):
        if block.hash != first_fork_hash:
            fork_blocks.append(block)
        else:
            break

    fork_blocks_json = jsonpickle.encode(fork_blocks)

    return json.dumps({"fork_blocks": fork_blocks_json})


# Fixme: Where this algorithm should be called?
def consensus():
    """
    Our naive consensus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    current_len = len(blockchain.chain)

    # Init flag
    flag = False

    for peer in peers:
        # Ask others for their blockchain
        response = requests.get('{}chain_by_hash'.format(peer))

        # Reformat from json
        length = response.json()['length']
        chain_hashes = jsonpickle.decode(response.json()['chain'])

        # If we do not have the longest chain, replace it
        if length > current_len:
            # Find the first block of the other's fork
            fork_hash = blockchain.first_fork_hash(chain_hashes)

            # Ask him for the blocks

            url = "{}get_block_from".format(peer)
            headers = {'Content-Type': "application/json"}
            data_json = {"first_fork_hash": jsonpickle.encode(fork_hash)}

            response = requests.post(url,
                                     data=data_json,
                                     headers=headers)

            # Take the a list of fork's block in json form
            fork_blocks_list_json = response.json()["fork_blocks"]

            # Decode them
            fork_blocks_list = jsonpickle.decode(fork_blocks_list_json)

            # Check if it is valid fork, if not continue asking the rest peers
            if blockchain.is_fork_valid(fork_blocks_list):
                # if so, include it in our chain
                blockchain.include_the_fork(fork_blocks_list)

                # Take the new length
                current_len = len(blockchain.chain)

                # And assign True in the flag
                flag = True

    # In case we still have the longest blockchain return False
    return flag


# -------------------------------------------- the above are fixed --------------------------------------------- #

# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.

# Fixme: this function it should be maybe internal and not an API

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    # app.run(host='127).0.0.1', port = ""

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    # app.run(host='127.0.0.1', port=port)
