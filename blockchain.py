from block import Block
from transaction import Transaction
import time


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self):

        self.unconfirmed_transactions = []

        self.dict_nodes_utxos = dict()

        self.chain = []

        # the address to other participating members of the network
        self.peers = []

    # Return a list with blockchain's transactions
    def get_transactions(self):
        # Init the list
        all_transactions = []

        # Iterate all the blockchain
        for block in self.chain:
            for transaction in block.transactions:
                all_transactions.append(transaction)

        # Return the list
        return all_transactions

    # Add a new transaction which is broadcasted
    def add_new_transaction(self, transaction):

        # Node's utxos list
        node_utxos = self.dict_nodes_utxos[transaction.sender_address]

        # Check if transaction is valid
        if not self.is_transaction_valid(transaction, node_utxos):
            return False

        # Add transaction into blockchain's unconfirmed transactions' list
        self.unconfirmed_transactions.append(transaction)

        # Fixme: capacity test

        return True

    @staticmethod
    def is_transaction_valid(transaction, sender_utxos):

        # First check if the signature is valid
        if not transaction.verify_transaction():
            return False

        # Check if the sender has the required utxos
        if not Blockchain.check_node_utxos_for_transaction(transaction, sender_utxos):
            return False

        # The transaction can be added to the new block
        return True

    # Check if the node has the required utxos and amount for this transaction
    @staticmethod
    def check_node_utxos_for_transaction(transaction, node_utxos):

        # Sum of transaction inputs
        total_input_amount = 0

        # Search every transaction input into node's utxos
        for transaction_input in transaction.transaction_inputs:
            transaction_output_id = transaction_input.previous_output_id

            utxo_taking_place = False

            # Find the transaction with this id into utxos
            for idx, o in enumerate(node_utxos):
                if o.outputTransactionId == transaction_output_id:
                    # Mark it as existed
                    utxo_taking_place = True
                    # Sum the total amount of coins from input transactions
                    total_input_amount = total_input_amount + o.amount

                    # Delete it so if someone is going to ude it again , it's going to return wrong
                    del node_utxos[idx]

                    break

            # Check if all input transactions are taking place
            if not utxo_taking_place:
                return False

        # Check if the sum of input transactions' coins are enough
        if total_input_amount < transaction.amount:
            return False

        return True

    def create_genesis_block(self, recipient_addr):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 1, nonce 0
        and a valid hash.
        """
        print("Start creating genesis block")

        # Transaction with sender's wallet address 0
        first_transaction = Transaction.generic(recipient_addr, 100 * 5, time.time())

        genesis_block = Block(len(self.chain), [first_transaction], 0, "1", 0)
        genesis_block.hash = genesis_block.compute_hash()

        print("Genesis block is created")

        if self.add_block(genesis_block):
            print("Genesis block is appended successfully into blockchain")
        else:
            print("Genesis block is NOT appended into blockchain")

    @staticmethod
    def is_fork_valid(list_of_new_blocks, last_hash, dict_nodes_utxos_by_block_id):

        # Take last hash
        last_hash = list_of_new_blocks[0].previous_hash

        # Take the utxos after the last addition
        dict_nodes_utxos = dict_nodes_utxos_by_block_id[last_hash]

        for block in list_of_new_blocks:

            # If this block id valid then update nodes' utxos and previous hash value
            if Blockchain.is_block_valid(block, last_hash, dict_nodes_utxos):

                # Then update nodes' utxos list
                dict_nodes_utxos = Blockchain.update_utxos_of_nodes(dict_nodes_utxos, block)

                # And the hash value
                last_hash = block.hash

            else:
                return False

        # Return True if all the new list of blocks can be added
        return True

    def include_the_fork(self, list_of_new_blocks, dict_nodes_utxos_by_block_id):

        # Take last hash
        last_hash = list_of_new_blocks[0].previous_hash

        # Take the last valid dict_nodes_utxos
        dict_nodes_utxos = dict_nodes_utxos_by_block_id[last_hash]

        # New chain initialization
        new_chain = []

        # Create new chain
        for block in self.chain:
            if block.previous_hash == last_hash:
                break
            else:
                new_chain.append(block)

        # Assign the new chain
        self.chain = new_chain

        # Add the new blocks into it
        for block in list_of_new_blocks:
            dict_nodes_utxos = self.add_block(block, dict_nodes_utxos)

            # Save the new dict_nodes_utxos
            dict_nodes_utxos_by_block_id[block.hash] = dict_nodes_utxos

        # Return the updated dict_nodes_utxos_by_block_id to node
        return dict_nodes_utxos_by_block_id



    @staticmethod
    def is_block_valid(block, previous_block_hash, dict_nodes_utxos):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """

        # Check if the previous has is the same with previous block's hash
        if previous_block_hash != block.previous_hash:
            return False

        # Check the proof of work
        if not Blockchain.is_valid_proof(block):
            return False

        # Check if all transactions in the new block are valid accordingly with the validity transaction's rules.
        if not Blockchain.check_validity_of_block_transactions(block, dict_nodes_utxos):
            return False

        return True

    def add_block(self, block, dict_nodes_utxos):

        # Take the utxos of all nodes after the addition of the last block
        # previous_block_hash = self.last_block().hash
        # dict_nodes_utxos = dict_nodes_utxos_by_block_id[previous_block_hash]

        # Then update nodes' utxos list and save the current state. Fixme: not sure if this supposed to be here
        self.dict_nodes_utxos = self.update_utxos_of_nodes(dict_nodes_utxos, block)

        # Update unconfirmed transactions and save the undone ones
        undone_transactions = self.update_unconfirmed_transactions()

        # Append it into blockchain
        self.chain.append(block)

        # Return the new current list of all nodes' utxos and the undone transactions
        return self.dict_nodes_utxos, undone_transactions

    @property
    def last_block(self):
        # Return last block of the blockchain
        return self.chain[-1]

    @classmethod
    def is_valid_proof(cls, block):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block.hash.startswith('0' * cls.difficulty) and
                block.hash == block.compute_hash())

    @staticmethod
    def check_validity_of_block_transactions(block, nodes_utxos):

        copy_of_all_nodes_utxos = nodes_utxos.copy()

        # Check the validity of each block's transaction
        for transaction in block.transactions:
            if not Blockchain.is_transaction_valid(transaction, copy_of_all_nodes_utxos):
                return False
            return True

    def update_unconfirmed_transactions(self):

        # Save temporary the list
        unconfirmed_transactions_to_be_updated = self.unconfirmed_transactions

        # Init the list
        self.unconfirmed_transactions = []

        # Add its transaction again so to gather if its possible to be accepted
        for unconfirmed_transaction in unconfirmed_transactions_to_be_updated:
            if self.add_new_transaction(unconfirmed_transaction):
                # If it is accepted, delete it.
                unconfirmed_transactions_to_be_updated.remove(unconfirmed_transaction)

        # Return a list of transactions which couldn't be accepted
        return unconfirmed_transactions_to_be_updated

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block()

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash,
                          nonce=0)

        # Find the correct nonce
        new_block.proof_of_work(Blockchain.difficulty)

        # Add new block in the chain
        self.add_block(new_block)

        # Init unconfirmed transactions' list
        self.unconfirmed_transactions = []

        return True

    @staticmethod
    def update_utxos_of_nodes(dict_of_utxos, block):

        print("Block with id: " + block.hash)

        # For every transaction in the block
        for transaction in block.transactions:

            print("Transaction with id: " + transaction.transaction_id)

            # Check if node is sender in this transaction
            if transaction.sender_address in dict_of_utxos:

                # Current node's address
                node_address = transaction.sender_address

                # Current node's utxos list
                nodes_utxos = dict_of_utxos[node_address]

                print("Transaction id: " + transaction.transaction_id +
                      "\n Node with address: " + transaction.sender_address + " is sender!")

                # Remove the input transaction from node's utxos list
                for transaction_input in transaction.transaction_inputs:
                    transaction_output_id = transaction_input.previous_output_id

                    # Find the transaction with this id into utxos and delete it
                    for idx, o in enumerate(nodes_utxos):
                        if o.outputTransactionId == transaction_output_id:
                            del nodes_utxos[idx]
                            break

                    # Add the output transaction to node's utxos list
                    for transaction_output in transaction.transaction_outputs:

                        # Find the correct transaction output
                        if transaction_output.recipient_address == node_address:
                            nodes_utxos.append(transaction_output)

                dict_of_utxos[node_address] = nodes_utxos  # update value

            # Check if node is receiver in this transaction
            if transaction.recipient_address in dict_of_utxos:

                # Current node's address
                node_address = transaction.sender_address

                # Current node's utxos list
                nodes_utxos = dict_of_utxos[node_address]

                print("Transaction id: " + transaction.transaction_id +
                      "\n Node with address: " + transaction.sender_address + " is receiver!")

                # Then add the correct output transaction to node's utxos list
                for transaction_output in transaction.transaction_outputs:

                    # Find the correct transaction output
                    if transaction_output.recipient_address == node_address:
                        nodes_utxos.append(transaction_output)

                dict_of_utxos[node_address] = nodes_utxos  # update value

        return dict_of_utxos

    # ----------------------------------------- Not used yet ------------------------------------------------- #

    def create_chain_from_dump(self, chain_dump):
        for idx, block_data in enumerate(chain_dump):
            if idx == 0:
                continue  # skip genesis block
            block = Block(block_data["index"],
                          block_data["transactions"],
                          block_data["timestamp"],
                          block_data["previous_hash"],
                          block_data["nonce"])

            block.hash = block_data['hash']

            added = self.add_block(block)
            if not added:
                raise Exception("The chain dump is tampered!!")

    @classmethod
    def check_chain_validity(cls, chain):

        # Init previous hash to "1" -- Genesis block's hash value
        previous_hash = "1"

        # Iterate all the blockchain
        for block in chain:

            # if the next condition doesn't hold then the block chain is not valid
            if not cls.is_valid_proof(block) or \
                    previous_hash != block.previous_hash:
                return False

            # Save block's hash to compare it with the next one
            previous_hash = block.hash

        return True

    def create_utxos_of_nodes(self, list_of_addresses, blockchain):

        # Create a dictionary of the utxos with key the address of its node in the given list.
        # And initiate it!
        dict_of_utxos = {}

        for address in list_of_addresses:
            # Init with an empty list
            dict_of_utxos[address] = []

        for block in blockchain:
            dict_of_utxos = self.update_utxos_of_nodes(dict_of_utxos, block)
