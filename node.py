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

        self.utxos = []




    def update_utxos(self, block: Block):

        print("Try to update node")

        node_address = self.wallet.public_key

        # For every transaction in the block
        for transaction in block.transactions:

            print("Transaction with id: " + transaction.transaction_id)

            # Check if node is sender in this transaction
            if node_address == transaction.sender_address:

                print("Node is sender in this transaction")

                # Remove the input transaction from node's utxos list
                for transaction_input in transaction.transaction_inputs:
                    transaction_output_id = transaction_input.previous_output_id

                    # Find the transaction with this id into utxos and delete it
                    for idx, o in enumerate(self.wallet.utxos):
                        if o.outputTransactionId == transaction_output_id:
                            del self.wallet.utxos[idx]
                            break

                    # Add the output transaction to node's utxos list
                    for transaction_output in transaction.transaction_outputs:

                        # Find the correct transaction output
                        if transaction_output.recipient_address == node_address:
                            self.wallet.utxos.append(transaction_output)

            # Check if node is receiver in this transaction
            if node_address == transaction.recipient_address:

                print("Node is receiver in this transaction")

                # Then add the correct output transaction to node's utxos list
                for transaction_output in transaction.transaction_outputs:

                    print("Transaction in the transaction_outputs list")

                    # Find the correct transaction output
                    if transaction_output.recipient_address == node_address:
                        self.wallet.utxos.append(transaction_output)
                        print("We found the correct transaction output and we add it")


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
