import logging
import os
import re
import sys
import time
from threading import Thread
from time import sleep

import click
import requests

import json

from node import Node
from wallet import Wallet
import jsonpickle
from blockchain import Blockchain

from rest import app

import global_variable


# !!! this is a comment intended for master branch ONLY !!!!
@click.command()
@click.option('-p', '--port', default=22147, help='port to run the client on')
@click.option('-b', '--bootstrap', is_flag=True, help='for bootstrap node only')
@click.option('-a', '--auto', is_flag=True, default=False,
              help='Everyone starts send coins automatically, after takes the initial coins')
def main(port, bootstrap, auto):
    # signal.signal(signal.SIGINT, sigint_handler())
    if bootstrap:
        print("This is bootstrap node")

        wallet = Wallet()

        global_variable.node = Node(0, wallet)

        # Add bootstrap node in the peers' list
        ip_address = global_variable.bootstrapIp
        public_key_str = wallet.public_key

        # Create tuple of register data
        node_register_data = (public_key_str, ip_address)

        # Append it in nodes peers' list
        global_variable.node.peers.append(node_register_data)

        # edw an theloume kanoume wait mexri olo oi clients na graftoun
        # giati to diktuo den exei arxikopoihthei akoma, ara de mporoume na kanoume
        # transactions
    else:
        print("This is user node")

        if register_with_bootstrap(port) is False:
            print("Problem establishing connecion -- exit")
            exit()

        # edw perimenoume anagastika na mas apantisei o bootstrap
        # to register request

    # ksekinaei se thread to loop pou diavazei input kai kalei
    # tis antistoixes sinartiseis tou node gia na parei
    # to balance, teleutaia transactions

    thr_client = Thread(target=client_input_loop)
    thr_client.start()

    thr_auto = Thread(target=send_coins_auto_after_initial_coins, args=[auto])
    thr_auto.start()

    logging.getLogger('werkzeug').disabled = True
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    app.run(host='0.0.0.0', port=port)

    thr_auto.join()
    thr_client.join()

    # exit()


def send_coins_auto_after_initial_coins(auto):
    # If chain has the genesis block wait 10sec and start auto paying

    node = global_variable.node

    # If auto is disable return
    if auto is False:
        return
    else:
        # Otherwise wait till the genesis block is sent and first of all, all users have been register!
        while len(node.blockchain.chain) < 1 and len(node.peers) == global_variable.numOfClients:
            sleep(1)

        # Wait for another 10sec, so the system be stabilized
        sleep(20)

        # Call the function which reads the transactions from a default file, and keep logs for verify
        test_case_1()


def sigint_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


def client_input_loop():  # maybe: ,node
    with app.app_context():
        # global node

        node = global_variable.node

        # node.print_balance()
        # node.wallet.balance(node.blockchain)
    # node = global_variable.node

    sleep(0.5)
    print("Client started...")
    while True:
        # str = input(f"[node{node.current_id_count}]>>")
        str_in = input("[node" + str(node.current_id_count) + "]>>")

        if str_in in {'balance', 'b'}:
            print("Balance: ", node.wallet.balance(node.blockchain))
        elif str_in.startswith('init'):
            init_nodes_coins()
        elif str_in.startswith('bl'):
            # print(node.blockchain)
            node.blockchain.print_transactions()
        elif str_in in {'view', 'v'}:
            print_view()
        elif str_in in {'help', 'h'}:
            print_help()
        elif str_in == 'test':
            test_case_1()
        elif str_in == 'test_v':
            test_case_1_verify()
        elif str_in.startswith('utxos'):
            node.blockchain.print_utxos()
        elif str_in.startswith('cutxos'):
            node.blockchain.print_utxos(1)
        elif str_in.startswith('tff'):
            transactions_from_default_file(node)
        elif str_in.startswith('tffs'):
            transactions_from_default_file_time_delay(node)
            # transactions_from_file(str, node)
        elif str_in.startswith('results'):
            write_results_to_file()
        elif str_in.startswith('t'):
            client_transaction(str_in, node)
        elif str_in.startswith('un'):
            print_unconfirmed()
        elif str_in in {'q', 'quit', 'e', 'exit'}:
            print("Exiting...")
            # exit()
            return

        elif str_in in {'\n', ''}:
            continue
        else:
            print_invalid_command()




def print_view():
    node = global_variable.node

    for transaction in node.blockchain.get_transactions():
        print(transaction)


def print_unconfirmed():
    node = global_variable.node

    for transaction in global_variable.node.blockchain.unconfirmed_transactions:
        print(transaction)


def write_results_to_file():
    node = global_variable.node

    chain_len = len(node.blockchain.chain)

    # Take the first block after the initial coins blocks
    idx = int((len(node.peers) - 1) / node.blockchain.capacity) + 1  # plus one because there is the genesis block
    first_block = node.blockchain.chain[idx]

    # From these block take the first transaction's timestamp
    first_transaction = first_block.transactions[0]
    first_transaction_timestamp = first_transaction.timestamp

    last_block = node.blockchain.last_block()
    last_block_timestamp = last_block.timestamp

    capacity = node.blockchain.capacity

    difficulty = node.blockchain.difficulty

    peers_len = len(node.peers)

    filename = "nodes_" + str(peers_len) + "_capacity_" + str(capacity) + "_difficulty_" + str(difficulty) + ".json"

    current_dir = os.getcwd()

    path_file = current_dir + "/result/" + filename

    if os.path.exists(path_file):
        os.remove(path_file)

    with open(path_file, 'w') as file:
        json.dump({"capacity": capacity,
                   "difficulty": difficulty,
                   "first_transaction_timestamp": first_transaction_timestamp,
                   "last_block_timestamp": last_block_timestamp,
                   "chain_len": chain_len}, file)


def init_nodes_coins():
    # Take the reference to global variance node
    node = global_variable.node

    # Send initial money to all other users
    for idx, peer in enumerate(node.peers):
        if not (global_variable.node.wallet.public_key == peer[0]):
            str_in = "t " + str(idx) + " 100"
            client_transaction(str_in, node)


def transactions_from_default_file(node):
    file_path = str(global_variable.numOfClients) + "nodes/transactions" + str(node.current_id_count) + ".txt"
    f = open(file_path, "r")
    for line in f:
        client_transaction("tff " + line, node)
        time.sleep(1)


def transactions_from_default_file_time_delay(node):
    file_path = str(global_variable.numOfClients) + "nodes/transactions" + str(node.current_id_count) + ".txt"
    f = open(file_path, "r")
    for line in f:
        client_transaction("tff " + line, node)
        time.sleep(3)


def transactions_from_file(str_in, node):
    args = str_in.split(' ')
    if len(args) != 2:
        print('usage: tff <filename>')
    else:
        f = open(args[1], "r")
        for line in f:
            client_transaction("tff " + line, node)


# This function is called so node to be registered and synced with bootstrap node
def register_with_bootstrap(my_port):
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    # Use the global variables

    # global node
    wallet = Wallet()
    # host_name = socket.gethostname()
    # host_name = socket.getfqdn()
    # ip = socket.gethostbyname(host_name)

    # my_url = "http://" + ip + ":" + str(my_port)
    #
    # print("my url for register is: " + my_url)

    # Init request's parameters
    public_key_json = jsonpickle.encode(wallet.public_key)
    data = {"public_key": public_key_json,
            "node_port": str(my_port)}
    headers = {'Content-Type': "application/json"}
    url = "{}/register_node".format(global_variable.bootstrapIp)

    # Make a request to register with remote node and obtain information
    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        # Decode json attributes
        chain_list = jsonpickle.decode(response.json()['chain'])
        peers = jsonpickle.decode(response.json()['peers'])

        # Search index of node's ip address
        node_id = [idx for idx, x in enumerate(peers) if x[0] == wallet.public_key][0]
        global_variable.peers_ids = {peers[i][0]: i for i, x in enumerate(peers)}

        try:
            global_variable.node = Node(node_id, wallet)

            node = global_variable.node

            node.blockchain = Blockchain.create_chain_from_list(chain_list)
            node.peers = peers

        except Exception as e:
            # if chain is tempered, then return False
            print(str(e))
            return False
        # Return True if blockchain is created
        return True
    else:
        # if something goes wrong, return wrong
        return False


# Sunarthsh gia na kanei o client transaction
# mporei na xrisimopoihsei tin sunartisi tou node
def client_transaction(str_in, node):
    args = str_in.split(" ")
    if len(args) != 3:
        print("Invalid transaction form. Should have exactly 2 arguments")
        print_transaction_help()
        return
    if not valid_pkey(args[1]):
        print("Invalid public key for transaction")
        print_transaction_help()
        return
    elif not valid_ammount(args[2]):
        print("Invalid amount of coins for transaction")
        print_transaction_help()
        return

    recipient_ids = [int(i) for i in args[1] if i.isdigit()]

    if len(recipient_ids) != 1:
        print("Found more than num in", recipient_ids)
    recipient_id = recipient_ids[0]
    if recipient_id > len(node.peers) - 1:
        print("Error: No node with this id: " + str(recipient_id))
        return
    amount = args[2]
    recipient_pubkey = node.peers[recipient_id][0]
    node.wallet.sendCoinsTo(recipient_pubkey, int(amount), node.blockchain, node.peers)
    # edw gia kathe peer IP kanme broadcast sto /new_transaction


def test_case_1():
    node = global_variable.node
    my_id = node.current_id_count
    infile = str(global_variable.numOfClients) + "nodes/transactions" + str(my_id) + ".txt"
    inf = open(infile)
    total_c = 0
    for line in inf:
        words = line.split(" ")
        recipient_id = int(re.sub("[^0-9]", "", words[0]))
        amount = int(words[1])
        recipient_pubkey = node.peers[recipient_id][0]

        node.wallet.sendCoinsTo(recipient_pubkey, int(amount), node.blockchain, node.peers)
        time.sleep(2)

        node.sent_transactions_test[(recipient_id, amount)] = False
        total_c += 1
    inf.close()


def test_case_1_verify():
    node = global_variable.node
    my_id = node.current_id_count
    infile = '5nodes/transactions%d.txt' % my_id
    inf = open(infile)
    total_c = 0
    for line in inf:
        words = line.split(" ")
        recipient_id = int(re.sub("[^0-9]", "", words[0]))
        amount = int(words[1])
        recipient_pubkey = node.peers[recipient_id][0]

        node.sent_transactions_test[(recipient_id, amount)] = False
        total_c += 1
    inf.close()
    my_sent_txs = node.sent_transactions_test
    outfile = 'logs/test1/test1_node%d.log' % my_id
    outf = open(outfile, 'w')

    for block in node.blockchain.chain:
        for transaction in block.transactions:
            my_pkey = node.peers[my_id][0]
            receiver = [idx for idx, peer in enumerate(node.peers) if peer[0] == transaction.recipient_address][0]
            # sender = [idx for idx, peer in enumerate(node.peers) if peer[0] == transaction.sender_address][0]
            if transaction.sender_address == my_pkey:
                if (receiver, transaction.amount) not in my_sent_txs:
                    s = "Error(test1): i see transaction i did not send! (%d to node%d)\n" % (
                        transaction.amount, receiver)
                    print(s, end='')
                    outf.write(s)
                else:
                    s = "Success(test1): i see transaction in block %d (%d to node%d)\n" % (
                        block.index, transaction.amount, receiver)
                    print(s, end='')
                    outf.write(s)
                    my_sent_txs[(receiver, transaction.amount)] = True
    c = 0
    for tx in my_sent_txs:
        if my_sent_txs[tx] == False:
            s = "Error(test1):I don't see in blockchain my transaction!(id%d %d)\n" % tx
            print(s, end='')
            outf.write(s)
            c += 1
    s = "test case 1 finish!! %d out of %d transactions sucessfull\n" % (total_c - c, total_c)
    print(s)
    outf.write(s)
    outf.close()


def print_help():
    print(
        '''
        Welcome to Noobcash!
        commands:
            t <recipient_address> <amount>      Transfer coins to public key specified
            tff                                 Transfer money from default file fast but unsafe
            tff                                 Transfer money from default file safer, but with a delay
            test                                Same as ttf but you can verify the results with test_v
            test_v                              Verify which transaction from the send ones is in the blockchain
            bl                                  Print all the blockchain
            results                             Rights the statistic results in the result folder (testing use)
            init                                Send initial money to all registered nodes if you are the bootstrap node
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


# -------------------------------- Not used yet -------------------------------- #


def valid_pkey(str):
    return True


def valid_ammount(str):
    return True


def print_balance():
    print("balance")




main()


def register_user_request(port):
    global node
    # kainourgio public & private key
    wallet = Wallet()
    public_key_json = jsonpickle.encode(wallet.public_key)
    url = global_variable.bootstrapIp
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
