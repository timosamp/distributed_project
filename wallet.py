import binascii

import Crypto
import Crypto.Random
import jsonpickle
import requests

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import global_variable
from transaction import Transaction, TransactionOutput
from block import Block

import hashlib
import json
import time
from urllib.parse import urlparse
from uuid import uuid4


class Wallet:

    def __init__(self):

        # Create a pair of private and public key
        self.private_key, self.public_key = self.create_RSA_pairKeys()

        # Set the public key as the wallet's adders
        self.address = self.public_key

        print("Wallet is created")

    def wallet_address(self):
        # Return the address of the wallet's owner
        return self.address

    def balance(self, blockchain):

        # Get nodes' utxos list from blockchain
        last_validated_dict_of_node = blockchain.get_valid_dict_nodes_utxos()

        # Check if sender there is in dict_nodes_utxos, and take it if so.
        if not (self.public_key in last_validated_dict_of_node):
            # Otherwise, assign an empty list
            utxos_dict = dict()
            print("I didn't find my self in utxos history :(")
        else:

            # lock for changing blockchain
            while not global_variable.reading_writing_blockchain.acquire(False):
                # print("False acquire blockchain lock")
                time.sleep(1)
                continue

            utxos_dict = last_validated_dict_of_node[self.public_key]

            # Release blockchain lock
            global_variable.reading_writing_blockchain.release()

        # Init the amount variable
        total_amount = 0

        # Iterate the utxos list and sum the whole available amount of the wallet
        for utxo_id in utxos_dict:
            total_amount += utxos_dict[utxo_id].amount

        # print("Wallet has balance: " + str(total_amount) + "\n")
        # print(blockchain)

        # Return the total amount
        return total_amount

    def sendCoinsTo(self, recipient_address, amount, blockchain, peers):
        # check if the sender have the amount which is trying to send (check balance)
        if self.balance(blockchain) < amount:
            return False

        # Collect a bunch of utxos with sum amount bigger than amount want to be sent

        # Init the sub list and utxos_amount
        sub_list_of_utxos = []
        utxos_amount = 0

        while not global_variable.reading_writing_blockchain.acquire(False):
            # print("False acquire blockchain lock")
            time.sleep(1)
            continue

        # Get node's utxos list from blockchain
        node_utxos_dict = blockchain.dict_nodes_utxos[self.public_key]

        # Release the blockchain lock
        global_variable.reading_writing_blockchain.release()

        # Iterate utxos' list and add their amount to the utxos_amount,
        # until the required amount is reached and append them into a sub list
        # which will be given to the new transaction.
        for utxo_id in node_utxos_dict:
            if utxos_amount < amount:
                utxos_amount += node_utxos_dict[utxo_id].amount
                sub_list_of_utxos.append(node_utxos_dict[utxo_id])

        # print("UTXOs has gathered from sender.")

        # Create a new transaction with receivers public key.
        # Sign this transaction with the private key of the sender's wallet.
        transaction = Transaction.with_utxos(self.public_key, recipient_address, amount, time.time(), sub_list_of_utxos)

        # Sign the transaction
        transaction.sign_transaction(self.private_key)
        #print("Transaction is signed.")

        Wallet.broadcast_transaction_to_peers(transaction, peers)

        # Return true if transaction creation and broadcast is finished successfully
        return True

    @staticmethod
    def broadcast_transaction_to_peers(transaction, peers):
        cntr = 0
        for (idx, (peer, peer_url)) in enumerate(peers):

            transaction_json = jsonpickle.encode(transaction)
            data = {"transaction": transaction_json}
            headers = {'Content-Type': "application/json"}
            url = "{}/new_transaction".format(peer_url)

            #print("url is: " + url)

            #print("")
            r = requests.post(url,
                              data=json.dumps(data),
                              headers=headers)
            if r.status_code == 200:
                #print("Broadcast to peer ", idx, " success!")
                # break # for consensus test
                cntr += 1
            else:
                #print("Error: broadcast to peer ", idx)
                x=1
        if cntr == len(peers):
            print("Broadcast to all peers successfull")

    @staticmethod
    def create_RSA_pairKeys():
        key = RSA.generate(2048)
        public_key = key.publickey().exportKey("PEM")
        private_key = key.exportKey("PEM")
        return private_key, public_key
