import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4


class wallet:

    def __init__(self):
        ##set

        # Create a pair of private and public key
        self.private_key, self.public_key = self.create_RSA_pairKeys()

        # Set the public key as the wallet's adders
        self.address = self.public_key

    # self.transactions

    # def balance():

    @staticmethod
    def create_RSA_pairKeys():
        key = RSA.generate(2048)
        public_key = key.publickey().exportKey("PEM")
        private_key = key.exportKey("PEM")
        return private_key, public_key
