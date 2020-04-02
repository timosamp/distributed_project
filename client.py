import string

import click
from node import Node
from rest import app

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
@click.option('-b', '--bootstrap', is_flag=True, help='for bootstrap node only', )
def initialize(port, bootstrap):
    if (bootstrap):
        print("This is bootstrap node")
        initialize_bootstrap(port)
    else:
        print("This is user node")
        initialize_user(port)

def initialize_bootstrap(port):
    node = Node(0)
    blockchain = node.blockchain
    app.run(host='127.0.0.1', port=port)

def initialize_user(port):
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




