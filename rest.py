# https://github.com/satwikkansal/python_blockchain_app/blob/master/node_server.py
from threading import Thread

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

# from test_threads_flask import node, app

import jsonpickle

import global_variable

# import client

app = Flask(__name__)
CORS(app)


# global_variable.initialize()

# global node
# .......................................................................................

# # create a node
# node = Node(0)

# Take the blockchain of node (import from client)
# blockchain = node.blockchain
# the address to other participating members of the network
# peers = node.peers

# node = global_variable.node


# get all transactions in the blockchain
@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    node = global_variable.node

    # lock for changing blockchain
    while not global_variable.reading_writing_blockchain.acquire(False):
        # print("False acquire blockchain lock")
        time.sleep(1)
        continue

    list_of_transactions = node.blockchain.get_transactions()

    # Release blockchain lock
    global_variable.reading_writing_blockchain.release()

    response = {'transactions': list_of_transactions}
    return jsonpickle.encode(response), 200
    # return jsonify(response), 200


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def receive_transaction_api():
    tx_data = request.get_json()

    transaction_thread = Thread(target=receive_transaction_thread, args=[tx_data])
    transaction_thread.start()

    return "Transaction received", 200


def receive_transaction_thread(tx_data):
    # print("--- Received transaction at API ----")
    while not global_variable.add_transaction.acquire(False):
        # print("False acquired transaction lock")
        time.sleep(1)
        continue

    print("add_transaction has started")

    node = global_variable.node

    # tx_data = request.get_json()

    if not tx_data.get("transaction"):
        return  # "Invalid json", 400

    # print(tx_data.get("transaction"))

    incoming_transaction = jsonpickle.decode(tx_data.get("transaction"))

    print("incoming transaction id: " + str(incoming_transaction.transaction_id[:20]))

    # print(incoming_transaction.recipient_address)

    # lock for changing blockchain
    while not global_variable.reading_writing_blockchain.acquire(False):
        # print("False acquire blockchain lock")
        time.sleep(1)
        continue

    node.blockchain.add_new_transaction(incoming_transaction)

    # Release blockchain lock
    global_variable.reading_writing_blockchain.release()

    # print("/new_transaction: ")
    # print(incoming_transaction)

    print("add_transaction has ended")

    global_variable.add_transaction.release()

    return  # "Success", 200


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def receive_block_api():
    block_data = request.get_json()

    block_thread = Thread(target=verify_and_add_block, args=[block_data])
    block_thread.start()

    return "Block received", 200


def verify_and_add_block(block_data):
    while not global_variable.add_block_lock.acquire(False):
        # print("False acquired block lock")
        time.sleep(1)
        continue

    print("add_block has started")

    node = global_variable.node

    # block_data = request.get_json()

    if not block_data.get("block"):
        return  # "Invalid json", 400

    # Decode block from json form
    incoming_block_json = block_data.get("block")

    # Decode object from json
    block = jsonpickle.decode(incoming_block_json)

    print("Incoming block's hash: " + str(block.hash[:20]))

    # Verify it
    verified = False

    # lock for changing blockchain
    while not global_variable.reading_writing_blockchain.acquire(False):
        # print("False acquire blockchain lock")
        time.sleep(1)
        continue

    # If block has the proof of work the continue with more checks.
    # If block doesn't have valid pow, discard it.
    if node.blockchain.is_valid_proof(block):

        print("block is valid proof")

        # Release the lock
        global_variable.reading_writing_blockchain.release()

        # lock for changing blockchain
        while not global_variable.reading_writing_blockchain.acquire(False):
            # print("False acquire blockchain lock")
            time.sleep(1)
            continue

        if node.blockchain.is_block_valid(block):

            print("block is valid generally")

            # Release the lock
            global_variable.reading_writing_blockchain.release()

            # Stop mining
            while not global_variable.flag_lock.acquire(False):
                print("False acquire mine lock")
                continue
            global_variable.node.mine_flag = False
            global_variable.flag_lock.release()

            # lock for changing blockchain
            while not global_variable.reading_writing_blockchain.acquire(False):
                # print("False acquire blockchain lock")
                time.sleep(1)
                continue

            # If the rest test succeed then add block into blockchain
            node.blockchain.add_block(block)
            node.blockchain.copy_of_myself = node.blockchain.chain
            # Release the lock
            global_variable.reading_writing_blockchain.release()

            # Change the flag for the corresponding response
            verified = True

        else:
            # Release the lock
            global_variable.reading_writing_blockchain.release()

            # If not, call the consesus algorithm to check
            # if there is longer valid chain available.
            consensus()

    # Release the lock
    if global_variable.reading_writing_blockchain.locked():
        global_variable.reading_writing_blockchain.release()

    print("add_block is released")
    global_variable.add_block_lock.release()

    if not verified:
        return  # "The block was discarded by the node", 201

    return  # "Block added to the chain", 200


# Endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to register a node
@app.route('/chain', methods=['GET'])
def get_node_data():
    node = global_variable.node

    chain_len = len(node.blockchain.chain)
    chain_json = jsonpickle.encode(node.blockchain.chain)
    node_peers_json = jsonpickle.encode(node.peers)

    return json.dumps({"length": chain_len,
                       "chain": chain_json,
                       "peers": node_peers_json})


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node = global_variable.node

    # Get node's public key

    req_data = request.get_json()

    # Get node's public
    public_key_json = req_data["public_key"]
    public_key = jsonpickle.decode(public_key_json)

    # Get node's ip address
    node_url = req_data["node_url"]

    # print("node_url: " + node_url)

    if (not public_key) or (not node_url):
        return "Invalid data", 400

    # Maybe it is useful
    # ip_address = request.remote_addr
    # remote_port = request.environ.get('REMOTE_PORT')
    # node_url = str(ip_address) + ":" + str(remote_port)

    # Build tuple for peer's list
    node_register_data = (public_key, node_url)

    # Add it into the peer's list
    # global node
    # node.peers.append(node_register_data)
    node.peers.append(node_register_data)

    # Fixme: check if node has already been registered
    while len(node.peers) < global_variable.numOfClients:
        time.sleep(0.5)  # wait 0.5 sec

    # Create a thread to send them the initial money,
    # just after the completion of their creation.
    thr_init_coins = Thread(target=transfer_initial_coins, args=[public_key])
    thr_init_coins.start()

    return get_node_data(), 200


def transfer_initial_coins(peer_public_key):
    # Take your node's object address
    node = global_variable.node

    # Wait for the nodes to be created
    time.sleep(5)

    # Send 100 coins to this node
    node.wallet.sendCoinsTo(peer_public_key, 100, node.blockchain, node.peers)
    # print(str(peer_public_key[25:40]))


# Get the chain only by hashes.
# This endpoint will be used by our app
# for find the longest chain in consesus algorithm
@app.route('/chain_by_hash', methods=['GET'])
def get_chain_by_hashes():

    node = global_variable.node

    # lock for changing blockchain
    while not global_variable.reading_writing_blockchain.acquire(False):
        # print("False acquire blockchain lock")
        time.sleep(1)
        continue

    chain_len = len(node.blockchain.chain)
    # print("chain is : ")
    # print(node.blockchain)

    chain_hashes = []

    for block in node.blockchain.chain:
        chain_hashes.append(block.hash)

    # Release the blockchain lock
    global_variable.reading_writing_blockchain.release()

    chain_hashes_json = jsonpickle.encode(chain_hashes)

    # global_variable.add_block_lock.release()

    return json.dumps({"length": chain_len,
                       "chain": chain_hashes_json})

# ### OLD CODE 124 ###
# @app.route('/get_block_from', methods=['POST'])
# def get_blocks_from():
#
#     node = global_variable.node
#
#     hash_data = request.get_json()
#
#     # Save first hash of node's fork
#     first_fork_hash = jsonpickle.decode(hash_data["first_fork_hash"])
#
#     # Init list
#     fork_blocks_reversed = []
#     fork_blocks = []
#
#     # Lock for changing blockchain
#     while not global_variable.reading_writing_blockchain.acquire(False):
#         # print("False acquire blockchain lock")
#         time.sleep(1)
#         continue
#
#     # Collect fork's block
#     for block in reversed(node.blockchain.chain):
#         if block.hash != first_fork_hash:
#             fork_blocks_reversed.append(block)
#         else:
#             fork_blocks_reversed.append(block)
#             break
#
#     # Release the blockchain lock
#     global_variable.reading_writing_blockchain.release()
#
#     for block in reversed(fork_blocks_reversed):
#         fork_blocks.append(block)
#
#     fork_blocks_json = jsonpickle.encode(fork_blocks)
#
#     return json.dumps({"fork_blocks": fork_blocks_json})
# ### END OLD CODE 124 ###

### new CODE 124 ###
@app.route('/get_block_from', methods=['POST'])
def get_blocks_from():

    node = global_variable.node

    hash_data = request.get_json()

    # Save first hash of node's fork
    first_fork_hash = jsonpickle.decode(hash_data["first_fork_hash"])

    # Init list
    fork_blocks_reversed = []
    fork_blocks = []

    # Lock for changing blockchain
    # while not global_variable.reading_writing_blockchain.acquire(False):
    #     # print("False acquire blockchain lock")
    #     time.sleep(1)
    #     continue

    # Collect fork's block
    for block in reversed(node.blockchain.copy_of_myself):
        if block.hash != first_fork_hash:
            fork_blocks_reversed.append(block)
        else:
            fork_blocks_reversed.append(block)
            break

    # Release the blockchain lock
    # global_variable.reading_writing_blockchain.release()

    for block in reversed(fork_blocks_reversed):
        fork_blocks.append(block)

    fork_blocks_json = jsonpickle.encode(fork_blocks)

    return json.dumps({"fork_blocks": fork_blocks_json})
### END new CODE 124 ###


# Fixme: Where this algorithm should be called?
def consensus():
    """
    Our naive consensus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """

    print("---- Entered Consensus ----")
    node = global_variable.node
    print("My blockchain:")
    node.blockchain.print_transactions()
    node.blockchain.copy_of_myself = node.blockchain.chain
    # lock for changing blockchain
    while not global_variable.reading_writing_blockchain.acquire(False):
        # print("False acquire blockchain lock")
        time.sleep(1)
        continue

    current_len = len(node.blockchain.chain)

    # Init the variables we'll use
    max_len = current_len
    peer_to_get_blocks = ""
    chain_hashes = []

    # Release blockchain lock
    global_variable.reading_writing_blockchain.release()

    # print("current len is : " + str(current_len))

    # Init flag
    flag = False

    for idx, peer in enumerate(node.peers):

        # peer = node.peers[-1]
        peer_url = peer[1]

        if global_variable.node.wallet.public_key == peer[0]:
            continue

        # Ask others for their blockchain
        response = requests.get('{}/chain_by_hash'.format(peer_url))

        # print(global_variable.node.blockchain)

        # Reformat from json
        length = response.json()['length']
        chain_hashes = jsonpickle.decode(response.json()['chain'])

        # print("length > current_len: " + str(length) + " " + str(current_len))

        # If we do not have the longest chain, replace it
        if length > max_len:  # >= current_len and current_len > 3:
            print("Node (%d) has bigger chain(%d) that us(%d)" % (idx, length, current_len))

            max_len = length
            peer_to_get_blocks = peer_url

        else:
            print("We had same length")
            print("Node (%d) has chain(%d) that us(%d)" % (idx, length, current_len))


    # If all has same length as as leave
    if max_len == current_len:
        print("--- Leaving consensus (flag=%d)" % flag)
        return flag


    # lock for changing blockchain
    while not global_variable.reading_writing_blockchain.acquire(False):
        # print("False acquire blockchain lock")
        time.sleep(1)
        continue

    # Find the first block of the other's fork
    fork_hash = node.blockchain.first_fork_hash(chain_hashes)
    # print("first diff id: " + str(fork_hash))

    # Release blockchain lock
    global_variable.reading_writing_blockchain.release()

    if fork_hash == "":
        # Then we just haven't taken the new block yet, wait.
        print("Then we just haven't taken the new block yet, wait.")
        return flag


    # Ask him for the blocks
    url = "{}/get_block_from".format(peer_to_get_blocks)
    headers = {'Content-Type': "application/json"}
    data_json = {"first_fork_hash": jsonpickle.encode(fork_hash)}

    response = requests.post(url,
                             data=json.dumps(data_json),
                             headers=headers)

    # Take the a list of fork's block in json form
    fork_blocks_list_json = response.json()["fork_blocks"]

    # Decode them
    fork_blocks_list = jsonpickle.decode(fork_blocks_list_json)
    print("\nBlocks from received blockchain are:")
    for b in fork_blocks_list:
        b.print_transactions()
    # print(fork_blocks_list)

    # lock for changing blockchain
    while not global_variable.reading_writing_blockchain.acquire(False):
        # print("False acquire blockchain lock")
        time.sleep(1)
        continue


    # Check if it is valid fork, if not continue asking the rest peers
    if node.blockchain.is_fork_valid(fork_blocks_list):
        print("--- fork is valid ---")
        # if so, include it in our chain
        node.blockchain.include_the_fork(fork_blocks_list)

        # And assign True in the flag
        flag = True

    # Release blockchain lock
    global_variable.reading_writing_blockchain.release()


    # In case we still have the longest blockchain return False
    print("--- Leaving consensus (flag=%d)" % flag)
    return flag

# -------------------------------------------- the above are fixed --------------------------------------------- #
