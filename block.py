import blockchain

import hashlib as hasher


class Block:
    def __init__(self, index, listOfTransaction, timestamp, previous_hash):

        """
        Constructor for the `Block` class.
        :param index:         Unique ID of the block.
        :param listOfTransaction:  List of transactions.
        :param timestamp:     Time of generation of the block.
        :param previous_hash: Hash of the previous block in the chain which this block is part of.
        """
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.listOfTransactions = listOfTransaction
        # self.hash = self.compute_block()

    def compute_block(self):
        # calculate self.hash
        sha = hasher.sha256()
        sha.update(str(self.index) +
                   str(self.listOfTransactions) +
                   str(self.timestamp) +
                   str(self.previous_hash))
        return sha.hexdigest()





# def add_transaction(transaction transaction, blockchain blockchain):
# add a transaction to the block
