from blockchain import Blockchain
from wallet import Wallet
from block import Block


class Node:
    def __init__(self, node_id: int):

        print("Start creating node with id: " + str(node_id))

        self.current_id_count = node_id

        self.wallet = Wallet()

        self.node_address = self.wallet.public_key

        self.blockchain = Blockchain()
        if node_id == 0:
            self.blockchain.create_genesis_block(self.node_address)

        self.peers = []

        dict_nodes_utxos = {}






    # def create_new_block(self):
    #     pass

    # create a wallet for this node, with a public key and a private key

    # def create_wallet(self):
    #     pass

    # def register_node_to_ring(self):
    #     pass
    #
    # # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    # # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
    #
    # def create_transaction(self, sender, receiver, signature):
    #     pass
    #
    # # remember to broadcast it
    #
    # def broadcast_transaction(self):
    #     pass
    #
    # def validate_transaction(self):
    #     pass
    #
    # # use of signature and NBCs balance
    #
    # def add_transaction_to_block(self):
    #     pass
    #
    # # if enough transactions  mine
    #
    # def mine_block(self):
    #     pass
    #
    # def broadcast_block(self):
    #     pass
    #
    # def valid_proof(self, katialloedw, difficulty):
    #     pass
    #
    # # concencus functions
    #
    # def valid_chain(self, chain):
    #     pass
    #
    # # check for the longer chain acroose all nodes
    #
    # def resolve_conflicts(self):
    #     pass
