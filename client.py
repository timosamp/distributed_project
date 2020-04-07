import string

import click
import requests

from node import Node
from rest import app
from wallet import Wallet
import jsonpickle

numOfClients = 5
bootstrapIp = "http://192.168.0.1"

def main():
    '''Welcome to noobcash!! Type \"help\" to view usage stuff'''
    initialize()
    while True:
        str = input(">>")
        if str == 'balance':
            print_balance()
        elif str == 'view':
            print_view()
        elif str == 'help':
            print_help()
        elif str.startswith('t'):
            transaction(str)
        elif str.startswith('q'):
            return
        else:
            invalid_command()


@click.command()
@click.option('-p', '--port', default=22147, help='port to run the client on')
@click.option('-b', '--bootstrap', is_flag=True, help='for bootstrap node only')
def initialize(port, bootstrap):
    app.run(host='127.0.0.1', port=port)
    if (bootstrap):
        print("This is bootstrap node")
        initialize_bootstrap(port)
    else:
        print("This is user node")
        initialize_user(port)


def initialize_bootstrap(port):
    node = Node(0)

def initialize_user(port):
    wallet = Wallet()
    public_key_json = jsonpickle.encode(wallet.public_key)
    url = bootstrapIp
    headers = {'Content-Type': "application/json"}
    print("Registering to bootstrap...")
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


def transaction(str):
    args = str.split(" ")
    if not valid_pkey(args[1]):
        print("Invalid public key for transaction")
        return
    elif not valid_ammount(args[2]):
        print("Invalid ammount of coins for transaction")
        return


def valid_pkey(str):
    return True


def valid_ammount(str):
    return True


def print_balance():
    print()


def print_view():
    print()


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


def invalid_command():
    print("Invalid command. Use \"help\" to view available options.")


main()
