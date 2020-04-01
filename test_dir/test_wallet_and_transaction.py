from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction
from block import Block
from node import Node

# create a node
node = Node(0)

# Take its blockchain
blockchain = node.blockchain

node.update_utxos(blockchain.last_block)
node

if node.wallet.sendCoinsTo("Timos", 50) is False:
    print("You doesn't have enough coins!")
