from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction
from block import Block
from node import Node

import json
from collections import namedtuple
from json import JSONEncoder


class StudentEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def customStudentDecoder(obj_dict):
    return namedtuple('X', obj_dict.keys())(*obj_dict.values())


# create a node
node = Node(0)

# Take its blockchain
blockchain = node.blockchain

node.wallet.balance(blockchain)

# node.wallet.update_utxos(blockchain.last_block)

if node.wallet.sendCoinsTo("Timos", 50, blockchain) is False:
    print("You doesn't have enough coins!")

node.wallet.balance(blockchain)
