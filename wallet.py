import binascii

import Crypto
import Crypto.Random

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from transaction import Transaction, TransactionOutput

import hashlib
import json
import time
from urllib.parse import urlparse
from uuid import uuid4


class Wallet:

    def __init__(self):

        # Create a pair of private and public key
        self.private_key, self.public_key, self.keys = self.create_RSA_pairKeys()

        # Set the public key as the wallet's adders
        self.address = self.public_key

        # list of unspent transactions - previous output transactions
        self.utxos = []

        print("Wallet is created")

    def wallet_address(self):
        # Return the address of the wallet's owner
        return self.address

    def balance(self):
        # Init the amount variable
        total_amount = 0

        # Iterate the utxos list and sum the whole available amount of the wallet
        for utxo in self.utxos:
            total_amount += utxo.amount

        print("Wallet with id:\n" + str(self.public_key) + "\nhas balance: " + str(total_amount))

        # Return the total amount
        return total_amount


    def sendCoinsTo(self, recipient_address, amount):
        # check if the sender have the amount which is trying to send (check balance)
        if self.balance() < amount:
            return False

        # Collect a bunch of utxos with sum amount bigger than amount want to be sent

        # Init the sub list and utxos_amount
        sub_list_of_utxos = []
        utxos_amount = 0

        # Iterate utxos' list, pop utxos and add their amount to the utxos_amount,
        # until the required amount is reached and append them into a sub list
        # which will be given to the new transaction.
        while utxos_amount < amount:
            utxo = self.utxos.pop()
            utxos_amount += utxo.amount
            sub_list_of_utxos.append(utxo)

        print("UTXOs has gathered from sender.")

        # Create a new transaction with receivers public key.
        # Sign this transaction with the private key of the sender's wallet.
        transaction = Transaction.with_utxos(self.address, recipient_address, amount, time.time(), sub_list_of_utxos)

        # Sign the transaction
        transaction.sign_transaction(self.keys)

        print("Transaction is signed.")

        # We need to add into wallet's utxos list the new transaction output for the change  #
        # The second instance into the list is the sender's output transaction               #
        #                                                                                    #
        # This line maybe shouldn't be here                                                  #
        # self.utxos.append(transaction.transaction_outputs[1])                              #
        # print("Transaction is added to the utxos' list")                                   #

        # FIXME: Broadcast the transaction to the whole network

        # Return true if transaction creation and broadcast is finished successfully
        return True

    @staticmethod
    def create_RSA_pairKeys():
        key = RSA.generate(2048)
        public_key = key.publickey().exportKey("PEM")
        private_key = key.exportKey("PEM")
        return private_key, public_key , key
