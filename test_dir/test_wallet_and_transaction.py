from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction
from block import Block
from node import Node

import json
import jsonpickle
from json import JSONEncoder




# create a node
node = Node(0)

# Take its blockchain
blockchain = node.blockchain

node.wallet.balance(blockchain)

# node.wallet.update_utxos(blockchain.last_block)

if node.wallet.sendCoinsTo("Timos", 50, blockchain) is False:
    print("You doesn't have enough coins!")

node.wallet.balance(blockchain)

print("--------------------------- block's test ---------------------------")


# Test for encode and decode object
randomblock = blockchain.chain[0]

blockJsonData = jsonpickle.encode(randomblock)
print(blockJsonData)

decRandomBlock = jsonpickle.decode(blockJsonData)
print(decRandomBlock)

print("--------------------------- List's test ---------------------------")

# Test encoding and decoding list of objects
listoftransacion = blockchain.unconfirmed_transactions

encodeList = jsonpickle.encode(listoftransacion)
print(encodeList)

decodedList = jsonpickle.decode(encodeList)
print(decodedList)

