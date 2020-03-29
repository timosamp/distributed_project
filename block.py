import blockchain

import hashlib as hasher


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):

        """
        Constructor for the `Block` class.
        :param index:         Unique ID of the block.
        :param transactions:  List of transactions.
        :param timestamp:     Time of generation of the block.
        :param previous_hash: Hash of the previous block in the chain which this block is part of.
        """
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.listOfTransactions = transactions
        # self.hash = self.compute_block()

    def compute_block(self):
        # calculate self.hash
        sha = hasher.sha256()
        sha.update(str(self.index) +
                   str(self.listOfTransactions) +
                   str(self.timestamp) +
                   str(self.previous_hash) +
                   str(self.nonce))
        return sha.hexdigest()

    # def compute_hash(self):
    #     """
    #     A function that return the hash of the block contents.
    #     """
    #     block_string = json.dumps(self.__dict__, sort_keys=True)
    #     return sha256(block_string.encode()).hexdigest()





# def add_transaction(transaction transaction, blockchain blockchain):
# add a transaction to the block
