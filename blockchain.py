from threading import Thread
from threading import Timer

import jsonpickle
import requests
import json

import global_variable
from block import Block
from transaction import Transaction
import time
import copy


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 3
    capacity = 2

    def __init__(self):

        self.unconfirmed_transactions = []

        self.dict_nodes_utxos = dict()

        self.dict_nodes_utxos_by_block_id = dict()

        self.chain = []

        # the address to other participating members of the network
        self.peers = []

        print("Blockchain is created")

        # self.timer = Timer(5.0, self.mine)

    """
        Returns the utxos for the 'last_block' of chain
    """

    def get_valid_dict_nodes_utxos(self):

        # Check if there is any block in blockchain
        if len(self.chain) > 0:
            # print("Chain is not empty")
            last_block = self.last_block()
            return self.dict_nodes_utxos_by_block_id[last_block.hash]
        else:
            # If it is empty return an empty dictionary
            return dict()

    # ----------------------------------------- Transaction's functions ----------------------------------------- #

    """
        Return a list with blockchain's transactions
    """
    def get_transactions(self):
        # Init the list
        all_transactions = []

        # Iterate all the blockchain
        for block in self.chain:
            for transaction in block.transactions:
                all_transactions.append(transaction)

        # Return the list
        return all_transactions


    """
        Add a new transaction to unconfirmed transactions(check if valid)
        If capacity is reached, start mine process
    """
    def add_new_transaction(self, transaction):

        # print("is alive? " + str(self.timer.is_alive()))
        # if self.timer.is_alive():
        #     self.timer.cancel()

        # Check if transaction is valid, and if so update the utxo list of sender
        if not self.is_transaction_valid(transaction, self.dict_nodes_utxos):
            # self.timer = Timer(5.0, self.mine)
            # self.timer.start()
            return False

        # update current utxos
        Blockchain.remove_input_transactions_from_node_utxos(transaction, self.dict_nodes_utxos)

        # If this line is available , node can use unconfirmed transactions
        Blockchain.add_output_transactions_to_node_utxos(transaction, self.dict_nodes_utxos)

        # Add transaction into blockchain's unconfirmed transactions' list
        self.unconfirmed_transactions.append(transaction)

        if len(self.unconfirmed_transactions) > self.capacity - 1:
            thr = Thread(target=self.mine)
            thr.start()
            # self.mine()

        # else:
            # self.timer = Timer(5.0, self.mine)
            # self.timer.start()
        return True


    """
        Check the transaction for correct hash(verify_transaction())
        Check the utxos of the sender if appropriate
        Add transaction outputs to dict_node_utxos
    """
    @staticmethod
    def is_transaction_valid(transaction, dict_nodes_utxos):

        # First check if the signature is valid
        if not transaction.verify_transaction():
            print("Transaction is not verified")
            return False
        print("Transaction is verified")

        # Check if the sender has the required utxos
        if not Blockchain.check_node_utxos_for_transaction(transaction, dict_nodes_utxos):
            return False
        print("Transaction is valid")

        # The transaction can be added to the new block
        return True

    """
        Check if the node has the required utxos and amount for this transaction
    """
    @staticmethod
    def check_node_utxos_for_transaction(transaction: Transaction, dict_nodes_utxos_init: dict):
        print("Check if sender has the required input transaction, and remove them from his utxo list")

        dict_nodes_utxos = copy.deepcopy(dict_nodes_utxos_init)

        # Check if sender there is already in the list, otherwise add him
        if not (transaction.sender_address in dict_nodes_utxos):
            dict_nodes_utxos[transaction.sender_address] = dict()

        sender_utxos = dict_nodes_utxos[transaction.sender_address]

        # Sum of transaction inputs
        total_input_amount = 0

        # Search every transaction input into node's utxos
        for transaction_input in transaction.transaction_inputs:
            transaction_output_id = transaction_input.previous_output_id

            # Check if input transactions are taking place
            if transaction_output_id in sender_utxos:
                total_input_amount = total_input_amount + sender_utxos[transaction_output_id].amount
                del sender_utxos[transaction_output_id]
            else:
                print("This input transaction is not in utxo list of sender")
                # Then return that the transaction wasn't successful
                return False


        # Check if the sum of input transactions' coins are enough
        if total_input_amount < transaction.amount:
            print("There are no enough transaction inputs")
            return False

        return True

# ----------------------------------------- Block's functions ----------------------------------------- #

    def first_fork_hash(self, chain_hashes_list):
        chain_hashes_set = set(chain_hashes_list)

        last_common_hash = ""
        first_dif_hash = ""


        # Find the last common hash
        for block in self.chain:
            print(str(block.hash) + " common?")
            if block.hash in chain_hashes_set:
                print("common: " + str(block.hash))
                last_common_hash = block.hash
            else:
                break

        print("Last common: " + str(last_common_hash))

        # Find first different hash of other's fork
        for block_hash in reversed(chain_hashes_list):
            if block_hash != last_common_hash:
                first_dif_hash = block_hash
            else:
                break

        print("first dif: " + str(first_dif_hash))

        # Return beginning of fork
        return first_dif_hash

    """
        Check if fork is valid
    """
    def is_fork_valid(self, list_of_new_blocks):
        if len(list_of_new_blocks) == 0:
            return True

        # Take last hash
        last_hash = list_of_new_blocks[0].previous_hash
        dict_nodes_utxos = self.dict_nodes_utxos_by_block_id[last_hash]

        for block in list_of_new_blocks:

            # If this block id valid then update nodes' utxos and previous hash value
            if self.is_block_valid(block, last_hash, dict_nodes_utxos):
                # print("Block is valid")

                # Then update nodes' utxos list and continue
                dict_nodes_utxos = Blockchain.update_utxos_of_nodes(dict_nodes_utxos, block)

                # And the hash value
                last_hash = block.hash

            else:
                print("Block is not valid")
                return False

        # Return True if all the new list of blocks can be added
        return True

# ----------------------------------------- Block's functions ----------------------------------------- #

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        print("Starting mining process..")
        if not self.unconfirmed_transactions:
            print("Stop mining process, empty list..")
            return False

        # Take first capacity unconfirmed transactions or block's mining.
        sub_list_of_unconfirmed = self.unconfirmed_transactions[:self.capacity]

        last_block = self.last_block()

        new_block = Block(index=last_block.index + 1,
                          transactions=sub_list_of_unconfirmed,
                          timestamp=time.time(),
                          previous_hash=last_block.hash,
                          nonce=0)

        # Find the correct nonce -- Fixme: mining parameter
        if new_block.proof_of_work(Blockchain.difficulty):
            # If mining is finished, continue:
            print("Success!! block is mined...")

            # Delete this first elements from self.unconfirmed_transactions.
            del self.unconfirmed_transactions[:self.capacity]
            #self.print_transactions()
            #print("--Mine is done--")

            # Fixme: broadcast block
            Blockchain.broadcast_block_to_peers(new_block)


            # Causing consensus
            # if not(len(self.chain) > 2 and len(self.chain) < 4):
            #     print("Now broacast")
            #     Blockchain.broadcast_block_to_peers(new_block)
            # else:
            #     global_variable.node.blockchain.add_block(new_block)


    """
        Create the genesis block
    """
    def create_genesis_block(self, recipient_addr):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 1, nonce 0
        and a valid hash.
        """
        print("\n\nGenesis block is created")

        print("Create genesis transaction")

        # Transaction with sender's wallet address 0
        first_transaction = Transaction.generic(recipient_addr, 100 * 5, time.time())

        genesis_block = Block(len(self.chain), [first_transaction], 0, "1", 0)
        genesis_block.hash = genesis_block.compute_hash()

        self.add_block(genesis_block)
        print("\n\n")


    def last_block(self):
        # Return last block of the blockchain
        return self.chain[-1]

    """
        Check validity of block. First check previous_block_hash
        then check all Transactions in Block    
    """
    def is_block_valid(self, block, previous_block_hash=None, dict_nodes_utxos=None):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """

        # If last_hash is None, take the hash of the last block
        if previous_block_hash is None:
            # If this block is the genesis
            if block.previous_hash == "1":
                # Then return true without validation
                #print("validate genesis block")
                return True

            # Otherwise, take as previous hash, the latest's hash value
            previous_block_hash = (self.last_block()).hash
        else:
            if previous_block_hash == "1":
                # Then return true without validation
                print("Validate genesis block")
                return True

        # If dict_nodes_utxos is None, then take the last valid list of utxos
        if dict_nodes_utxos is None:
            dict_nodes_utxos = self.dict_nodes_utxos_by_block_id[(self.last_block()).hash]

        # Check if the previous has is the same with previous block's hash
        if previous_block_hash != block.previous_hash:
            print("False previous hash")
            return False

        # Check the proof of work
        if not Blockchain.is_valid_proof(block):
            print("False pow hash")
            return False

        # Check if all transactions in the new block are valid accordingly with the validity transaction's rules.
        if not Blockchain.check_validity_of_block_transactions(block, dict_nodes_utxos):
            print("Block has invalid transactions")
            return False

        return True



    @classmethod
    def is_valid_proof(cls, block):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        # If this block is the genesis
        if block.previous_hash == "1":
            print("pow genesis block")
            print(block.hash)
            print(block.compute_hash())
            print(block.compute_hash())

            return block.hash == block.compute_hash()
        else:
            return (block.hash.startswith('0' * cls.difficulty) and
                    block.hash == block.compute_hash())


    def add_block(self, block, dict_of_fork_beginning=None):
        # Save the new dict_nodes_utxos into history with key the new block's id.
        # This new dict occurred by the utxo's that the node has validated before
        # the addition of the last block.

        if len(self.chain) == 0:
            # if we are adding genesis block consider history dictionary empty
            last_validated_dict_nodes_utxos = dict()
        else:
            if dict_of_fork_beginning is None:
                last_validated_dict_nodes_utxos = self.dict_nodes_utxos_by_block_id[(self.last_block()).hash]
            else:
                last_validated_dict_nodes_utxos = dict_of_fork_beginning

        # Update last valid history dictionary of utxos
        current_validated_dict_nodes_utxos = self.update_utxos_of_nodes(last_validated_dict_nodes_utxos, block)

        # Append it into history dict
        self.dict_nodes_utxos_by_block_id[block.hash] = copy.deepcopy(current_validated_dict_nodes_utxos)
        self.dict_nodes_utxos = copy.deepcopy(current_validated_dict_nodes_utxos)


        # Update unconfirmed transactions
        self.update_unconfirmed_transactions()

        # Append it into blockchain
        self.chain.append(block)

        print("Block is added in chain")


    @staticmethod
    def check_validity_of_block_transactions(block, dict_nodes_utxos):
        # Make a copy because Blockchain.is_transaction_valid is going to alter the list
        copy_of_all_nodes_utxos = copy.deepcopy(dict_nodes_utxos)

        # Check the validity of each block's transaction
        for transaction in block.transactions:
            if not Blockchain.is_transaction_valid(transaction, copy_of_all_nodes_utxos):
                return False
            return True

    def update_unconfirmed_transactions(self):
        print("Update of unconfirmed transactions")

        # Save temporary the list
        unconfirmed_transactions_to_be_updated = copy.deepcopy(self.unconfirmed_transactions)

        # Init the list
        self.unconfirmed_transactions = []

        # Add its transaction again so to gather if its possible to be accepted
        for unconfirmed_transaction in unconfirmed_transactions_to_be_updated:
            self.add_new_transaction(unconfirmed_transaction)


    @staticmethod
    def broadcast_block_to_peers(block):

        print("Broadcast starts")
        cntr = 0
        peers = global_variable.node.peers
        #print("Broadcasting block to peers")
        for (idx, (peer, peer_url)) in enumerate(list(reversed(peers))):

            block_json = jsonpickle.encode(block)
            data = {"block": block_json}
            headers = {'Content-Type': "application/json"}
            url = "{}/add_block".format(peer_url)

            #print("Broadcast to: " + peer_url)

            r = requests.post(url,
                              data=json.dumps(data),
                              headers=headers)
            if r.status_code == 200:
                #print("Broadcast to peer ", idx, " success!")
                # break # consesus -- fixme: after testing
                cntr += 1
            else:
                print("Error: broadcast to peer ", idx)
        if cntr == len(peers):
            print("Broadcasted block to all peers")
        else:
            print("Error broadcasting block.")

    @staticmethod
    def update_utxos_of_nodes(dict_of_utxos, block):

        dict_of_utxos_copy = copy.deepcopy(dict_of_utxos)
        # print("Block with id: " + block.hash)

        # For every transaction in the block
        for transaction in block.transactions:
            Blockchain.remove_input_transactions_from_node_utxos(transaction, dict_of_utxos_copy)
            Blockchain.add_output_transactions_to_node_utxos(transaction, dict_of_utxos_copy)

        #print("Update utxos ended\n")
        return dict_of_utxos_copy



    @staticmethod
    def remove_input_transactions_from_node_utxos(transaction: Transaction, dict_nodes_utxos: dict):
        print("Remove the required input transactions from sender's utxo list")

        # Check if sender there is already in the list, otherwise add him
        if not (transaction.sender_address in dict_nodes_utxos):
            dict_nodes_utxos[transaction.sender_address] = dict()

        sender_utxos = dict_nodes_utxos[transaction.sender_address]

        # Search every transaction input into node's utxos
        for transaction_input in transaction.transaction_inputs:
            transaction_output_id = transaction_input.previous_output_id
            if transaction_output_id in sender_utxos:
                del sender_utxos[transaction_output_id]


    @staticmethod
    def add_output_transactions_to_node_utxos(transaction: Transaction, dict_nodes_utxos):
        print("Add the output transactions in the corresponding node's utxo list")

        # Then add the correct output transaction to node's utxos list
        for transaction_output in transaction.transaction_outputs:

            # Current node's address
            node_address = transaction_output.recipient_address

            # Check if receiver there is already in the list, otherwise add him
            if not (node_address in dict_nodes_utxos):
                dict_nodes_utxos[node_address] = dict()

            # Current node's utxos dict
            nodes_utxos = dict_nodes_utxos[node_address]

            # Update his utxos from output transactions
            nodes_utxos[transaction_output.outputTransactionId] = transaction_output


    @classmethod
    def create_chain_from_list(cls, chain):

        print("Create temp block chain")

        # Init a blockchain list
        blockchain = Blockchain()

        for block in chain:
            if blockchain.is_block_valid(block) is True:
                blockchain.add_block(block)
            else:
                raise Exception("The chain dump is tampered!!")

        return blockchain

    # ----------------------------------------- Not used yet ------------------------------------------------- #

    @classmethod
    def print_utxos_of_nodes(cls, dict_nodes_utxos):
        print("\n\nPrint utxos of all nodes\n")
        i = 0
        for node_id in dict_nodes_utxos:
            print("Node " + str(i) + " has these utxos:\n")
            for utxo_id in dict_nodes_utxos[node_id]:
                print(dict_nodes_utxos[node_id][utxo_id].outputTransactionId)
            i = i + 1
        print("\nEnd printing\n\n")


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

    def print_utxos(self, flag = 0):
        print("--- Nodes' utxo lists ---")

        if flag == 1:
            last_valid_dict = self.dict_nodes_utxos
        else:
            last_valid_dict = self.get_valid_dict_nodes_utxos()

        for node_id in last_valid_dict:
            utxo_dict = last_valid_dict[node_id]
            print('\t+ Node %s... :' % node_id[27:40])
            for utxo_id in utxo_dict:
                print('\t\tutxo id: %s...' % utxo_dict[utxo_id].outputTransactionId[:20])



    def print_transactions(self):
        print("--- Blockchain ---")
        for idx, block in enumerate(self.chain):
            print('\t--- Block %d (hash: %s)' % (idx, block.hash))
            for tx in block.transactions:
                print('\t\tid:%s, \t%d' % (tx.transaction_id[0:10], tx.amount))

    def __str__(self):
        ret = "\n---Blockchain(blocks:" + str(len(self.chain)) + ")---\n"
        for block in self.chain:
            ret += (str(block) + "\n")
        return ret
