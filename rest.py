# https://github.com/satwikkansal/python_blockchain_app/blob/master/node_server.py

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

import jsonpickle

app = Flask(__name__)
CORS(app)

# .......................................................................................

# create a node
node = Node(0)
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

    tx_data = request.get_json()




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


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


# @app.route('/register_with', methods=['POST'])
# def register_with_existing_node():
#     """
#     Internally calls the `register_node` endpoint to
#     register current node with the node specified in the
#     request, and sync the blockchain as well as peer data.
#     """
#     node_address = request.get_json()["node_address"]
#     if not node_address:
#         return "Invalid data", 400
#
#     data = {"node_address": request.host_url}
#     headers = {'Content-Type': "application/json"}
#
#     # Make a request to register with remote node and obtain information
#     response = requests.post(node_address + "/register_node",
#                              data=json.dumps(data), headers=headers)
#
#     if response.status_code == 200:
#         global blockchain
#         global peers
#         # update chain and the peers
#         chain_dump = response.json()['chain']
#         blockchain = create_chain_from_dump(chain_dump)
#         peers.update(response.json()['peers'])
#         return "Registration successful", 200
#     else:
#         # if something goes wrong, pass it on to the API response
#         return response.content, response.status_code


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []

    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


# Fixme: Where this algo should be called?
def consensus():
    """
    Our naive consensus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for peer in peers:
        # Ask others for their blockchain
        response = requests.get('{}chain'.format(peer))

        # Reformat from json
        length = response.json()['length']
        chain = response.json()['chain']

        # If we do not have the longest chain, replace it
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        # Fixme: we copy all the block chain object or only the chain
        blockchain.chain = longest_chain
        return True

    # In case we still have the longest blockchain return False
    return False


# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
