import blockchain
import global_variable

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

        to_be_hashed = (str(self.index) +
                        # str(self.transactions) + # fixme: wrong
                        str(self.timestamp) +
                        str(self.nonce) +
                        str(self.previous_hash))

        # calculate block hash value
        sha = SHA.new(to_be_hashed.encode())

        return sha.hexdigest()

    def proof_of_work(self, difficulty):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        self.nonce = 0

        # Init mine_flag
        global_variable.flag_lock.acquire(True)
        global_variable.node.mine_flag = True
        global_variable.flag_lock.release()

        computed_hash = self.compute_hash()
        while not computed_hash.startswith('0' * difficulty):

            # Check if mining is stopped
            if not global_variable.node.mine_flag:
                # Then return False -- the mining process is interrupted by new block
                return False

            self.nonce += 1
            computed_hash = self.compute_hash()

        self.hash = computed_hash

        # Re-enable the mine_flag
        global_variable.flag_lock.acquire(True)
        global_variable.node.mine_flag = False
        global_variable.flag_lock.release()

        return True

    def to_dict(self):
        # Init the list of dictionaries
        list_of_transaction_dict = []

        # Create all the sub dictionaries of transactions and append them into the list
        for transaction in self.transactions:
            list_of_transaction_dict.append(transaction.to_dict())

        # Create the dictionary of the instance
        dict_of_block = self.__dict__

        # Correct to value of the transaction's list
        dict_of_block["transactions"] = list_of_transaction_dict

        return dict_of_block

    def __str__(self):
        ret = "Block(transactions:" + str(len(self.transactions)) + ") with id:" + self.hash + "\n"
        for t in self.transactions:
            ret += ("\t" + str(t) + "\n")
        return ret

    def print_transactions(self):
        print("Block %d", self.index)
        for tx in self.transactions:
            print('\t\tid:%s, \t%d' % (tx.transaction_id[0:10], tx.amount))
    @classmethod
    def build_from_dict(cls):
        # Fixme: not completed
        return

# def add_transaction(transaction transaction, blockchain blockchain):
# add a transaction to the block
