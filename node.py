from blockchain import Blockchain
from wallet import Wallet
from block import Block


class Node:
    def __init__(self, node_id, wallet: Wallet):

        print("\n\nStart creating node with id: " + str(node_id))

        self.current_id_count = node_id

        self.wallet = wallet

        self.node_address = self.wallet.public_key

        self.blockchain = Blockchain()

        self.mine_flag = False

        self.mine_cnt = 0

        if node_id == 0:
            self.blockchain.create_genesis_block(self.node_address)

        self.peers = list()

        self.peers_ids = dict()

        self.sent_transactions_test = dict()

