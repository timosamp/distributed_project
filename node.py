import block
import wallet


class node:
    def __init__(self):
        self.NBC = 100;

    ##set

    # self.chain
    # self.current_id_count
    # self.NBCs
    # self.mywallet = wallet

    # slef.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance

    def create_new_block(self):
        pass

    def create_wallet(self):
        pass

    # create a wallet for this node, with a public key and a private key

    def register_node_to_ring(self):
        pass

    # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs

    def create_transaction(self, sender, receiver, signature):
        pass

    # remember to broadcast it

    def broadcast_transaction(self):
        pass

    def validdate_transaction(self):
        pass

    # use of signature and NBCs balance

    def add_transaction_to_block(self):
        pass

    # if enough transactions  mine

    def mine_block(self):
        pass

    def broadcast_block(self):
        pass

    def valid_proof(self, katialloedw, difficulty):
        pass

    # concencus functions

    def valid_chain(self, chain):
        pass

    # check for the longer chain accroose all nodes

    def resolve_conflicts(self):
        pass
# resolve correct chain
