from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random

from Crypto.Hash import SHA
from Crypto.Hash.SHA import SHA1Hash
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, recipient_address, amount, utxos=None, sender_private_key=None):

        # self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = sender_address

        # self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.recipient_address = recipient_address

        # self.amount: το ποσό που θα μεταφερθεί
        self.amount = amount

        # self.transaction_inputs: λίστα από Transaction Input (ids)
        if utxos is not None:
            self.transaction_inputs = self.create_list_of_input_transactions(utxos)
        else:
            self.transaction_inputs = {}

        # self.transaction_outputs: λίστα από Transaction Output
        if utxos is not None:
            self.transaction_outputs = self.create_list_of_output_transactions(utxos)
        else:
            self.transaction_outputs = {}

        # create the hash/id of the transaction -- το hash του transaction
        self.transaction_id = self.transaction_hash()

        # selfSignature - I'm not sure if this suppose to be here
        if sender_private_key is not None:
            self.transaction_signature = self.sign_transaction(sender_private_key)
        else:
            self.transaction_signature = "First Transaction"

    # def to_dict(self):
    #     pass

    def sign_transaction(self, key):
        """
        Sign transaction with private key
        """

        # Create a hash value of the whole message
        sha_hash = SHA.new(str(self.sender_address) +
                           str(self.recipient_address) +
                           str(self.amount) +
                           str(self.transaction_inputs) +
                           str(self.transaction_outputs) +
                           str(self.transaction_id))

        # Construct an instance of the crypto object
        cipher = PKCS1_v1_5.new(key)

        # Create and return the signature
        return cipher.sign(sha_hash)

    def transaction_hash(self):
        sha = SHA.new()
        sha.update(str(self.sender_address) +
                   str(self.recipient_address) +
                   str(self.amount) +
                   str(self.transaction_inputs) +
                   str(self.transaction_outputs))
        return sha.hexdigest()

    def create_list_of_output_transactions(self, utxos):

        # Create recipient's output transaction
        receiver_output_transaction = TransactionOutput(self.transaction_id, self.recipient_address, self.amount)

        # compute first the total amount of the utxos
        utxos_amount = 0
        for utxo in utxos:
            utxos_amount += utxo.amount

        # Then compute sender's change
        change = utxos_amount - self.amount

        # FIXME: Check if the wallet has the required amount of money -- change >= 0

        # Create sender's output transaction
        sender_output_transaction = TransactionOutput(self.transaction_id, self.sender_address, change)

        # return the set of the output transactions
        return {receiver_output_transaction, sender_output_transaction}

    @staticmethod
    def create_list_of_input_transactions(utxos):

        # Init a set - list
        input_transactions = set()

        # Create the input transactions and append them into a list - set
        for utxo in utxos:
            input_transactions.add(TransactionInput(utxo.outputTransactionId))

        # Return the list of input_transactions
        return input_transactions


class TransactionOutput:
    def __init__(self, transaction_id, recipient_address, amount):
        self.transaction_id = transaction_id
        self.recipient_address = recipient_address
        self.amount = amount
        self.outputTransactionId = self.output_transaction_hash()

    def output_transaction_hash(self):
        # Create id of output transaction by hashing
        sha = SHA.new(str(self.transaction_id) +
                      str(self.recipient_address) +
                      str(self.amount))
        return sha.hexdigest()


class TransactionInput:
    def __init__(self, _previous_output_id):
        previous_output_id = _previous_output_id
