import binascii

import Crypto
import Crypto.Random

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

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
        # Init the amount variable
        total_amount = 0

        # Get node's utxos list from blockchain
        last_validated_dict_of_node = blockchain.get_valid_dict_nodes_utxos()
        utxos = last_validated_dict_of_node[self.public_key]
        # utxos = blockchain.dict_nodes_utxos[self.public_key]

        print("Balance:")
        print(utxos)

        # Iterate the utxos list and sum the whole available amount of the wallet
        for utxo in utxos:
            total_amount += utxo.amount

        print("Wallet has balance: " + str(total_amount))

        # Return the total amount
        return total_amount


    def sendCoinsTo(self, recipient_address, amount, blockchain):
        # check if the sender have the amount which is trying to send (check balance)
        if self.balance(blockchain) < amount:
            return False

        # Collect a bunch of utxos with sum amount bigger than amount want to be sent

        # Init the sub list and utxos_amount
        sub_list_of_utxos = []
        utxos_amount = 0

        # Get node's utxos list from blockchain
        node_utxos = blockchain.dict_nodes_utxos[self.public_key]

        # Iterate utxos' list and add their amount to the utxos_amount,
        # until the required amount is reached and append them into a sub list
        # which will be given to the new transaction.

        for utxo in node_utxos:
            if utxos_amount < amount:
                utxos_amount += utxo.amount
                sub_list_of_utxos.append(utxo)

        print("Sublist of utxos")
        print(sub_list_of_utxos)


        print("UTXOs has gathered from sender.")

        print("construct transaction -- public key is: ")
        print(self.public_key)

        # Create a new transaction with receivers public key.
        # Sign this transaction with the private key of the sender's wallet.
        transaction = Transaction.with_utxos(self.public_key, recipient_address, amount, time.time(), sub_list_of_utxos)

        print("inputs: ")
        print(transaction.transaction_inputs)

        # Sign the transaction
        transaction.sign_transaction(self.private_key)

        print("Transaction is signed.")

        print("history")
        print(blockchain.get_valid_dict_nodes_utxos()[self.public_key])

        # Add transaction into blockchain
        blockchain.add_new_transaction(transaction)

        print("history")
        print(blockchain.get_valid_dict_nodes_utxos()[self.public_key])

        # FIXME: Broadcast the transaction to the whole network

        # Return true if transaction creation and broadcast is finished successfully
        return True


    @staticmethod
    def create_RSA_pairKeys():
        key = RSA.generate(2048)
        public_key = key.publickey().exportKey("PEM")

        print("create public key: --------- @@@@@")
        print(public_key)

        private_key = key.exportKey("PEM")
        return private_key, public_key
