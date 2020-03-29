import blockchain

import time
import hashlib as hasher


class Block:
    def __init__(self, index, nonce, listOfTransaction, previous_hash):

        # Timestamp of block creation
        self.timestamp = time.time()

        # The hash number of the previous block
        self.previousHash = previous_hash

        self.nonce = nonce

        self.listOfTransactions = listOfTransaction

        self.hash = self.hash_block()

        def hash_block():
            # calculate self.hash
            sha = hasher.sha256()
            sha.update(str(self.index) +
                       str(self.timestamp) +
                       str(self.data) +
                       str(self.previous_hash))
            return sha.hexdigest()

# def myHash:


# def add_transaction(transaction transaction, blockchain blockchain):
# add a transaction to the block
