import string
from threading import Thread
from time import sleep

import click
import flask
import requests
from flask import Flask
from flask_cors import CORS

import json

from node import Node
from wallet import Wallet
import jsonpickle
from blockchain import Blockchain

# app = Flask(__name__)
# CORS(app)

from rest import app

numOfClients = 5
bootstrapIp = "http://127.0.0.1:22147"

global node


@click.command()
@click.option('-p', '--port', default=22147, help='port to run the client on')
@click.option('-b', '--bootstrap', is_flag=True, help='for bootstrap node only')
def main(port, bootstrap):

    if bootstrap:
        print("This is bootstrap node")

        wallet = Wallet()

        global node
        node = Node(0, wallet)
        # edw an theloume kanoume wait mexri olo oi clients na graftoun
        # giati to diktuo den exei arxikopoihthei akoma, ara de mporoume na kanoume
        # transactions
    else:
        print("This is user node")

        if register_with_bootstrap() is False:
            print("Problem establishing connecion -- exit")
            exit()

        # edw perimenoume anagastika na mas apantisei o bootstrap
        # to register request

    # ksekinaei se thread to loop pou diavazei input kai kalei
    # tis antistoixes sinartiseis tou node gia na parei
    # to balance, teleutaia transactions
    thr = Thread(target=client_input_loop, args=[])
    thr.start()
    app.run(host='127.0.0.1', debug=True, port=port)

    thr.join()


def client_input_loop():  # maybe: ,node
    with app.app_context():
        # global node

        # node.print_balance()
        node.wallet.balance(node.blockchain)

    sleep(0.5)
    print("Client started...")
    while True:
        str = input(">>")
        if str in {'balance', 'b'}:
            node.print_balance()
        elif str in {'view', 'v'}:
            node.print_view()
        elif str in {'help', 'h'}:
            print_help()
        elif str.startswith('t'):
            client_transaction(str)
        elif str in {'q', 'quit', 'e', 'exit'}:
            print("Exiting...")
            return
        elif str == "\n":
            continue
        else:
            print_invalid_command()


# This function is called so node to be registered and synced with bootstrap node
def register_with_bootstrap():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    # Use the global variables

    # global node
    wallet = Wallet()
    global bootstrapIp

    # Init request's parameters
    data = {"public_key": str(wallet.public_key)}
    headers = {'Content-Type': "application/json"}
    url = "{}/register_node".format(bootstrapIp)

    # Make a request to register with remote node and obtain information
    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:

        # Try to update chain
        chain_list = jsonpickle.decode(response.json()['chain'])
        peers = response.json()['peers']

        # Search index of node's ip address
        node_id = (idx for idx, x in enumerate(peers) if x[0] == wallet.public_key)

        try:


            # Then create a node
            global node
            node = Node(node_id, wallet)

            print("Node has created")

            # And try to create blockchain
            node.blockchain = Blockchain.create_chain_from_list(chain_list)

            print("Blockchain is created")

            # Update peers list
            node.peers.update(response.json()['peers'])
            print("Peers has updated")

        except Exception as e:

            # if chain is tempered, then return False
            print(str(e))
            return False

        # Return True if blockchain is created
        return True
    else:
        # if something goes wrong, return wrong
        return False


def register_user_request(port):
    global node
    # kainourgio public & private key
    wallet = Wallet()
    public_key_json = jsonpickle.encode(wallet.public_key)
    url = bootstrapIp
    headers = {'Content-Type': "application/json"}
    print("Registering to bootstrap...")
    # edw perimenoume apantisi apo bootstrap gia to id mas, peers, blockchain(me prwto block)
    # stelnoume to public key mas
    r = requests.post(url,
                      data=public_key_json,
                      headers=headers)
    data = r.json()
    peers = jsonpickle.decode(data['results'][0]['peers'])
    blockchain = jsonpickle.decode(data['results'][0]['blockchain'])
    node_id = data['results'][0]['node_id']

    node = Node(node_id)
    node.blockchain = blockchain
    node.peers = peers
    return


# Sunarthsh gia na kanei o client transaction
# mporei na xrisimopoihsei tin sunartisi tou node
def client_transaction(str):
    args = str.split(" ")
    if args.length != 3:
        print("Invalid transaction form")
        print_transaction_help()
    if not valid_pkey(args[1]):
        print("Invalid public key for transaction")
        print_transaction_help()
        return
    elif not valid_ammount(args[2]):
        print("Invalid ammount of coins for transaction")
        print_transaction_help()
        return
    print("transaction")
    # edw gia kathe peer IP kanoume broadcast sto /new_transaction


def valid_pkey(str):
    return True


def valid_ammount(str):
    return True


def print_balance():
    print("balance")


def print_view():
    print("view")


def print_help():
    print(
        '''
        Welcome to Noobcash!
        commands:
            t <recipient_address> <amount>      Transfer coins to public key specified
            view                                View previous transactions
            balance                             View wallet balance
            help                                Print this help message
            q                                   Quit
        '''
    )


def print_invalid_command():
    print("Invalid command. Use \"help\" to view available options.")


def print_transaction_help():
    print("t <recipient_address> <amount>      Transfer coins to public key specified")


main()
