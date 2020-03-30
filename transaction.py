from collections import OrderedDict

import binascii
import hashlib

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, recipient_address, amount, transaction_inputs, sender_private_key):
        ##set

        # self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = sender_address

        # self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.receiver_address = recipient_address

        # self.amount: το ποσό που θα μεταφερθεί
        self.amount = amount

        # self.transaction_id: το hash του transaction

        # self.transaction_inputs: λίστα από Transaction Input (ids)
        self.transaction_inputs = transaction_inputs

        # self.transaction_outputs: λίστα από Transaction Output
        self.transaction_outputs

        # create the hash/id of the transaction
        self.transaction_id = self.transaction_hash()

        # selfSignature - I'm not sure if this suppose to be here


        pass

    def to_dict(self):
        pass

    def sign_transaction(self, key):
        """
        Sign transaction with private key
        """
        pass

    def transaction_hash(self):
        sha = hashlib.sha256
        sha.update(str(self.sender_address) +
                   str(self.receiver_address) +
                   str(self.amount) +
                   str(self.transaction_inputs) +
                   str(self.transaction_outputs))
        return sha.hexdigest()


class TransactionOutput:
    def __init__(self, transaction_id, recipient_address, amount):
        self.transaction_id = transaction_id
        self.recipient_address = recipient_address
        self.amount = amount
        self.outputTransactionId = self.output_transaction_hash()

    def output_transaction_hash(self):
        sha = hashlib.sha256
        sha.update(str(self.transaction_id) +
                   str(self.recipient_address) +
                   str(self.amount))
        return sha.hexdigest()


class TransactionInput:
    def __init__(self, _previous_output_id):
        previous_output_id = _previous_output_id
