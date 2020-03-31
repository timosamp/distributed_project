import blockchain

from Crypto.Hash import SHA


class Block:
    # Class variable for the capacity of the block
    capacity = 10

    # constructor of the class
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        """
        Constructor for the `Block` class.
        :param index:         Unique ID of the block.
        :param transactions:  List of transactions.
        :param timestamp:     Time of generation of the block.
        :param previous_hash: Hash of the previous block in the chain which this block is part of.
        :param nonce: by default 0.
        """
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.transactions = transactions
        self.hash = ""  # self.compute_hash()

    def compute_hash(self):
        # calculate block hash value
        sha = SHA.new(str(self.index) +
                      str(self.transactions) +
                      str(self.timestamp) +
                      str(self.nonce) +
                      str(self.previous_hash))
        return sha.hexdigest()

# def add_transaction(transaction transaction, blockchain blockchain):
# add a transaction to the block
