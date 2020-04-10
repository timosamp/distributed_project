from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random

from Crypto.Hash import SHA256
from Crypto.Hash.SHA import SHA1Hash
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, recipient_address, amount, timestamp,
                 transaction_inputs=[], transaction_outputs=[], signature=None):

        # Timestamp of the creation
        self.timestamp = timestamp

        # self.sender_address: To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = sender_address

        # print("public key: ----------------")
        # print(str(self.sender_address))

        # self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.recipient_address = recipient_address

        # self.amount: το ποσό που θα μεταφερθεί
        self.amount = amount

        # create the hash/id of the transaction -- το hash του transaction
        self.transaction_id = self.transaction_hash()

        # self.transaction_inputs: λίστα από Transaction Input (ids)
        self.transaction_inputs = transaction_inputs

        # self.transaction_outputs: λίστα από Transaction Output
        self.transaction_outputs = transaction_outputs

        # selfSignature - I'm not sure if this suppose to be here
        if signature is not None:
            self.transaction_signature = signature
        else:
            self.transaction_signature = "Not signed"

    def to_dict(self):

        # Create a list of dictionaries of transaction inputs
        list_of_dict_transaction_inputs = []
        for transaction_input in self.transaction_inputs:
            list_of_dict_transaction_inputs.append(transaction_input.__dict__)

        # Create a list of dictionaries of transaction outputs
        list_of_dict_transaction_outputs = []
        for transaction_output in self.transaction_outputs:
            list_of_dict_transaction_outputs.append(transaction_output.__dict__)

        # Create the object's dictionary
        transaction_dict = self.__dict__

        # Change the values of the two list so they could be recoverable
        transaction_dict["transaction_outputs"] = list_of_dict_transaction_outputs
        transaction_dict["transaction_inputs"] = list_of_dict_transaction_inputs

        # Return the dictionary
        return transaction_dict

    @classmethod
    def build_from_dict(cls):
        # Fixme: not completed
        return

    @classmethod
    def with_utxos(cls, sender_address, recipient_address, amount, timestamp, utxos):

        print("Create transaction with utxos' list")

        # create transaction
        transaction = Transaction(sender_address, recipient_address, amount, timestamp)

        print("Transaction's object has created")

        # self.transaction_inputs: λίστα από Transaction Input (ids)
        transaction.create_list_of_input_transactions(utxos)

        print("Inputs Transaction list is created")
        print(transaction.transaction_inputs)

        # self.transaction_outputs: λίστα από Transaction Output
        transaction.create_list_of_output_transactions(utxos)

        print("Outputs Transaction list is created")

        print(transaction.transaction_outputs)

        return transaction

    @classmethod
    def generic(cls, recipient_address, amount, timestamp):

        print("Start creating generic transaction")

        # create transaction
        transaction = Transaction("", recipient_address, amount, timestamp)

        # Create the transaction_outputs list with only one Output Transaction
        transaction.transaction_outputs = [TransactionOutput(transaction.transaction_id, recipient_address, amount)]

        print("Generic transaction is created")

        return transaction

    def sign_transaction(self, private_key):
        """
        Sign transaction with private key
        """

        to_be_hashed = (str(self.timestamp) +
                        str(self.sender_address) +
                        str(self.recipient_address) +
                        str(self.amount) +
                        # str(self.transaction_inputs) +
                        # str(self.transaction_outputs) +
                        str(self.transaction_id))

        # Create a hash value of the whole message
        sha_hash = SHA256.new(to_be_hashed.encode())

        # Import private key
        key = RSA.importKey(private_key)

        print(sha_hash)

        # Construct an instance of the crypto object
        cipher = PKCS1_v1_5.new(key)

        # Create and return the signature
        self.transaction_signature = cipher.sign(sha_hash)

    def verify_transaction(self):
        # Fixme: it will appear an error for the key

        print("Internal verification function")

        to_be_hashed = (str(self.timestamp) +
                        str(self.sender_address) +
                        str(self.recipient_address) +
                        str(self.amount) +
                        # str(self.transaction_inputs) +
                        # str(self.transaction_outputs) +
                        str(self.transaction_id))

        # Create a hash value of the whole message
        sha_hash = SHA256.new(to_be_hashed.encode())

        # print("before_key")
        # print(self.sender_address)

        key = RSA.importKey(self.sender_address)

        # print("after_key")

        verifier = PKCS1_v1_5.new(key)

        # print("before_return_ver")

        return verifier.verify(sha_hash, self.transaction_signature)

    def verify_transaction_fully(self, blockchain, utxos):
        # Check the SHA-256 hash of transaction
        if not self.verify_transaction():
            return False

        # Check every input transaction for corresponding utxo
        # and remove it from utxos
        sender_utxos = utxos[self.sender_address]
        for tx_in in self.transaction_inputs:
            utxo = (tx_out for tx_out in sender_utxos if tx_in.previous_output_id == tx_out.outputTransactionId)
            if utxo is None:
                return False
            else:
                sender_utxos.remove(utxo)
        return True

    def transaction_hash(self):

        to_be_hashed = (str(self.timestamp) +
                        str(self.sender_address) +
                        str(self.recipient_address) +
                        str(self.amount))
        # str(self.transaction_inputs) +
        # str(self.transaction_outputs))

        sha = SHA256.new(to_be_hashed.encode())  # 'utf-8'

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

        # Create sender's output transaction
        sender_output_transaction = TransactionOutput(self.transaction_id, self.sender_address, change)

        # return the set of the output transactions
        self.transaction_outputs = {receiver_output_transaction, sender_output_transaction}

    def create_list_of_input_transactions(self, utxos):

        # Init a set - list
        input_transactions = []

        # Create the input transactions and append them into a list - set
        for utxo in utxos:
            input_transactions.append(TransactionInput(utxo.outputTransactionId))
            # Fixme: here we could mark these input transactions so they can not be used for other transactions
            # Or maybe delete them .

        # Return the list of input_transactions
        self.transaction_inputs = input_transactions

    def __str__(self):
        return f"Transaction with id: {self.transaction_id}\n\tSender: {self.sender_address}" \
               f"\n\tAmount: {self.amount}"


class TransactionOutput:
    def __init__(self, transaction_id, recipient_address, amount):
        self.transaction_id = transaction_id
        self.recipient_address = recipient_address
        self.amount = amount
        self.outputTransactionId = self.output_transaction_hash()

    def output_transaction_hash(self):
        # Value/String to be hashed
        to_be_hashed = (str(self.transaction_id) +
                        str(self.recipient_address) +
                        str(self.amount))

        # Create id of output transaction by hashing
        sha = SHA256.new(to_be_hashed.encode())

        return sha.hexdigest()


class TransactionInput:
    def __init__(self, _previous_output_id):
        self.previous_output_id = _previous_output_id
