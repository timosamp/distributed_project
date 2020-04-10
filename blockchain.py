from threading import Thread

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

    # Get last valid utxos dictionary
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

    # Add a new transaction which is broadcasted
    """
        Add a new transaction to unconfirmed transactions(check if valid)
        If capacity is reached, start mine process
    """

    def add_new_transaction(self, transaction):

        # print("Add new transaction into blockchain")
        # print("print utxos before adding")
        # for node_id in self.dict_nodes_utxos:
        #     for utxo in self.dict_nodes_utxos[node_id]:
        #         print(utxo.outputTransactionId)
        # print("End printing")

        # Check if transaction is valid, and if so update the utxo list of sender
        if not self.is_transaction_valid(transaction, self.dict_nodes_utxos):
            return False

        # print("Transaction is valid")

        # Add transaction into blockchain's unconfirmed transactions' list
        self.unconfirmed_transactions.append(transaction)

        # print("len of un transactions: " + str(len(self.unconfirmed_transactions)))

        if len(self.unconfirmed_transactions) > self.capacity - 1:
            thr = Thread(target=self.mine)
            thr.start()
            # self.mine()

        return True

    """
        Check the transaction for correct hash(verify_transaction())
        Check the utxos of the sender if appropriate
        Add transaction outputs to dict_node_utxos
    """

    @staticmethod
    def is_transaction_valid(transaction, dict_nodes_utxos):

        # print("Is_transaction_verified?")

        # First check if the signature is valid
        if not transaction.verify_transaction():
            #print("transaction is not verified")
            return False

        #print("Transaction is verified")

        # Node's utxos list
        sender_utxos = dict_nodes_utxos[transaction.sender_address]

        # Check if the sender has the required utxos
        if not Blockchain.check_node_utxos_for_transaction(transaction, sender_utxos):
            return False

        #print("Transaction has the required utxos")

        # So transaction has valid inputs and it's valid itself,
        # then append in according node's utxos its output transaction.
        # This way, the rest transactions in this block can use them as input.
        Blockchain.add_outputs_of_transaction_in_node_utxos(dict_nodes_utxos, transaction)
        #print("Output transactions has added successfully")

        # The transaction can be added to the new block
        return True

    @staticmethod
    def add_outputs_of_transaction_in_node_utxos(dict_of_utxos, transaction: Transaction):

        # Add valid transaction's outputs in according node's utxos list
        for transaction_output in transaction.transaction_outputs:

            # Take receivers' address
            receiver_address = transaction_output.recipient_address

            # If this node there isn't in dict_of_utxos,
            # add him and assign an empty list
            if not (receiver_address in dict_of_utxos):
                dict_of_utxos[receiver_address] = []

            # append in his utxos the output transaction
            dict_of_utxos[receiver_address].append(transaction_output)

    """
        Check if the node has the required utxos and amount for this transaction
    """

    @staticmethod
    def check_node_utxos_for_transaction(transaction: Transaction, sender_utxos: list):

        # Sum of transaction inputs
        total_input_amount = 0

        # Temporary list of used utxos
        temp_utxos_list = []

        # Search every transaction input into node's utxos
        for transaction_input in transaction.transaction_inputs:
            transaction_output_id = transaction_input.previous_output_id

            # print("Checking input transaction: " + transaction_output_id)

            utxo_taking_place = False

            # Find the transaction with this id into utxos
            for idx, o in enumerate(sender_utxos):

                # print("output: " + o.outputTransactionId)

                if o.outputTransactionId == transaction_output_id:
                    # Mark it as existed
                    utxo_taking_place = True
                    # Sum the total amount of coins from input transactions
                    total_input_amount = total_input_amount + o.amount

                    # Save the input value in a temporary list, so it can be recoverable if the transaction
                    # not be accepted.
                    temp_utxos_list.append(sender_utxos[idx])

                    # Delete it so if someone is going to ude it again , it's going to return wrong
                    del sender_utxos[idx]

                    break

            # Check if all input transactions are taking place
            if not utxo_taking_place:
                #print("Need utxos from unconfirmed transactions")

                # if not, recover the utxo list of node
                sender_utxos.extend(temp_utxos_list)

                # Then return that the transaction wasn't successful
                return False

        # Check if the sum of input transactions' coins are enough
        if total_input_amount < transaction.amount:
            print("There are no enough transaction inputs")
            print(total_input_amount)

            # if not, recover the utxo list of node
            sender_utxos.extend(temp_utxos_list)

            # And return that the transaction wasn't successful
            return False

        return True

    """
        Create the genesis block
    """

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

        # print(genesis_block.hash)

        print("Genesis block is created")

        self.add_block(genesis_block)
        print("Genesis block is appended successfully into blockchain")

    """
        Return the first hash before the fork
    """

    def first_fork_hash(self, chain_hashes_list):

        chain_hashes_set = set(chain_hashes_list)

        last_common_hash = ""
        first_common_hash = ""
        first_dif_hash = ""

        # print("find last common")
        # Find the last common hash
        # for block in reversed(self.chain):
        #     # print(str(block.hash))
        #     if block.hash in chain_hashes_set:
        #         # print("common: " + str(block.hash))
        #         first_common_hash = block.hash
        #     else:
        #         break
        #
        # # Find first different hash
        # for block_hash in reversed(chain_hashes_list):
        #     if block_hash != first_common_hash:
        #         first_dif_hash = block_hash
        #     else:
        #         break

        # Find the last common hash
        for block in self.chain:
            print(str(block.hash))
            if block.hash in chain_hashes_set:
                print("common: " + str(block.hash))
                last_common_hash = block.hash
            else:
                break

        # Find first different hash of other's fork
        for block_hash in reversed(chain_hashes_list):
            if block_hash != last_common_hash:
                first_dif_hash = block_hash
            else:
                break


        # Return beginning of fork
        return first_common_hash

    """
        Check if fork is valid
    """

    def is_fork_valid(self, list_of_new_blocks):

        if len(list_of_new_blocks) == 0:
            return True

        # Take last hash
        last_hash = list_of_new_blocks[0].previous_hash

        # Take the utxos after the last addition
        if last_hash == "1":
            dict_nodes_utxos = dict()
        else:
            dict_nodes_utxos = self.dict_nodes_utxos_by_block_id[last_hash]

        for block in list_of_new_blocks:

            # If this block id valid then update nodes' utxos and previous hash value
            if self.is_block_valid(block, last_hash, dict_nodes_utxos):
                print("Block is valid")

                # Then update nodes' utxos list
                dict_nodes_utxos = Blockchain.update_utxos_of_nodes(dict_nodes_utxos, block)

                # And the hash value
                last_hash = block.hash

            else:
                print("Block is not valid")
                return False

        # Return True if all the new list of blocks can be added
        return True

    """
        Change chain after fork
    """

    def include_the_fork(self, list_of_new_blocks):

        # Take last hash
        last_hash = list_of_new_blocks[0].previous_hash

        # New chain initialization
        new_chain = []

        # Create new chain -- copy the common part of the two blockchains into a new one
        for block in self.chain:
            if block.previous_hash == last_hash:
                break
            else:
                new_chain.append(block)

        # Assign the new chain
        self.chain = new_chain

        # Take the last valid dict_nodes_utxos and replace the current one
        self.dict_nodes_utxos = copy.deepcopy(self.dict_nodes_utxos_by_block_id[last_hash])
        # dict_of_fork_beginning = copy.deepcopy(self.dict_nodes_utxos)

        # Add the new blocks into it
        for block in list_of_new_blocks:

            last_hash = block.previous_hash

            dict_of_fork_beginning = copy.deepcopy(self.dict_nodes_utxos_by_block_id[last_hash])

            self.add_block(block, dict_of_fork_beginning)

        #print(self)
        # Return the updated dict_nodes_utxos_by_block_id to node
        # return self.dict_nodes_utxos_by_block_id

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
                print("validate genesis block")
                return True

        # If dict_nodes_utxos is None, then take the last valid list of utxos
        if dict_nodes_utxos is None:
            dict_nodes_utxos = self.dict_nodes_utxos_by_block_id[(self.last_block()).hash]

        # Check if the previous has is the same with previous block's hash
        if previous_block_hash != block.previous_hash:
            print("false previous hash")
            return False

        # Check the proof of work
        if not Blockchain.is_valid_proof(block):
            print("false pow hash")
            return False

        # Check if all transactions in the new block are valid accordingly with the validity transaction's rules.
        if not Blockchain.check_validity_of_block_transactions(block, dict_nodes_utxos):
            print("Block has invalid transactions")
            return False

        return True

    def add_block(self, block, dict_of_fork_beginning=None):

        # Then update nodes' utxos list and save the current state.
        # print("print utxos before update")
        # for node_id in self.dict_nodes_utxos:
        #     for utxo in self.dict_nodes_utxos[node_id]:
        #         print(utxo.outputTransactionId)
        # print("End printing")

        # if dict_of_fork_beginning is None:
        #     self.dict_nodes_utxos = self.update_utxos_of_nodes(self.dict_nodes_utxos, block)
        # else:
        #     self.dict_nodes_utxos = self.update_utxos_of_nodes(dict_of_fork_beginning, block)

        self.dict_nodes_utxos = self.update_utxos_of_nodes(self.dict_nodes_utxos, block)

        #print("print utxos after update")
        for node_id in self.dict_nodes_utxos:
            for utxo in self.dict_nodes_utxos[node_id]:
                #print(utxo.outputTransactionId)
                x=1
        #print("End printing")

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

        # print("history")
        # print(self.dict_nodes_utxos_by_block_id[block.hash])

        # Update unconfirmed transactions
        self.update_unconfirmed_transactions()

        # Append it into blockchain
        self.chain.append(block)

        #print("list length: " + str(len(self.chain)))

        # Return the new current list of all nodes' utxos
        # return self.dict_nodes_utxos

    def last_block(self):
        # Return last block of the blockchain
        return self.chain[-1]

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

    @staticmethod
    def check_validity_of_block_transactions(block, dict_nodes_utxos):

        # Make a copy because Blockchain.is_transaction_valid is going to alter the list
        copy_of_all_nodes_utxos = copy.deepcopy(dict_nodes_utxos)

        # print(block.transactions)

        # Check the validity of each block's transaction
        for transaction in block.transactions:
            # print("check transaction's validity")
            # print(transaction)
            if not Blockchain.is_transaction_valid(transaction, copy_of_all_nodes_utxos):
                return False
            return True

    def update_unconfirmed_transactions(self):

        #print("Update of unconfirmed transactions")

        # Save temporary the list
        unconfirmed_transactions_to_be_updated = copy.deepcopy(self.unconfirmed_transactions)

        # Init the list
        self.unconfirmed_transactions = []

        # Add its transaction again so to gather if its possible to be accepted
        for unconfirmed_transaction in unconfirmed_transactions_to_be_updated:
            self.add_new_transaction(unconfirmed_transaction)

        #print("len: " + str(len(self.unconfirmed_transactions)))
        #print("End of unconfirmed transactions")

        # If it is accepted, delete it.
        # unconfirmed_transactions_to_be_updated.remove(unconfirmed_transaction)

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        print("Starting mining process..")
        if not self.unconfirmed_transactions:
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
            # print(self)
            #print("New block:", new_block)
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

        # Add new block in the chain
        # self.add_block(new_block)

    @staticmethod
    def broadcast_block_to_peers(block):
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
                cntr +=1
                x=1
            else:
                x=1
                print("Error: broadcast to peer ", idx)
        if cntr == len(peers):
            print("Broadcasted block to all peers")
        else:
            print("Error broadcasting block.")

    @staticmethod
    def update_utxos_of_nodes(dict_of_utxos, block):

        dict_of_utxos_copy = copy.deepcopy(dict_of_utxos)

        #print("Update utxos start\n")

        # print("print utxos before update")
        # i = 0
        # for node_id in dict_of_utxos_copy:
        #     print("node " + str(i))
        #     for utxo in dict_of_utxos_copy[node_id]:
        #         print(utxo.outputTransactionId)
        #     i = i + 1
        # print("End printing")

        # print("Block with id: " + block.hash)

        # For every transaction in the block
        for transaction in block.transactions:

            # print("Transaction with id: " + transaction.transaction_id)

            # ----------------------------- update utxos for sender ----------------------------- #

            # Current node's address
            node_address = transaction.sender_address

            # Check if sender there is already in the list, otherwise add him
            if not (node_address in dict_of_utxos_copy):
                dict_of_utxos_copy[node_address] = []

            # Current node's utxos list
            nodes_utxos = dict_of_utxos_copy[node_address]

            # Remove the input transaction from node's utxos list
            for transaction_input in transaction.transaction_inputs:
                transaction_output_id = transaction_input.previous_output_id

                # print("used: " + transaction_output_id)

                # Find the transaction with this id into utxos and delete it
                for idx, o in enumerate(nodes_utxos):
                    if o.outputTransactionId == transaction_output_id:
                        # print("delete: " + nodes_utxos[idx].outputTransactionId)
                        del nodes_utxos[idx]
                        break

            # Add the output transaction to node's utxos list
            for transaction_output in transaction.transaction_outputs:
                # print("generate: " + transaction_output.outputTransactionId)

                # Find the correct transaction output
                if transaction_output.recipient_address == node_address:

                    # If there is already in the list don't add it.
                    it_is_in = False
                    for utxo in nodes_utxos:
                        if utxo.outputTransactionId == transaction_output.outputTransactionId:
                            it_is_in = True

                    if not it_is_in:
                        nodes_utxos.append(transaction_output)

            # ----------------------------- update utxos for receiver ----------------------------- #

            # Current node's address
            node_address = transaction.recipient_address

            # Check if receiver there is already in the list, otherwise add him
            if not (node_address in dict_of_utxos_copy):
                dict_of_utxos_copy[node_address] = []

            # Current node's utxos list
            nodes_utxos = dict_of_utxos_copy[node_address]

            # Then add the correct output transaction to node's utxos list
            for transaction_output in transaction.transaction_outputs:

                # Find the correct transaction output
                if transaction_output.recipient_address == node_address:

                    # If there is already in the list don't add it.
                    it_is_in = False
                    for utxo in nodes_utxos:
                        if utxo.outputTransactionId == transaction_output.outputTransactionId:
                            it_is_in = True

                    if not it_is_in:
                        nodes_utxos.append(transaction_output)

            # print("\nprint utxos after update")
            # i = 0
            # for node_id in dict_of_utxos_copy:
            #     print("node " + str(i))
            #     for utxo in dict_of_utxos_copy[node_id]:
            #         print(utxo.outputTransactionId)
            #     i = i + 1
            # print("End printing\n")

        #print("Update utxos ended\n")
        return dict_of_utxos_copy

    @classmethod
    def create_chain_from_list(cls, chain):

        # Init a blockchain list
        blockchain = Blockchain()

        #print("Create temp block chain")

        for block in chain:

            # print(" into loop ")

            if blockchain.is_block_valid(block) is True:

                # print("Try to add block")

                blockchain.add_block(block)
            else:
                raise Exception("The chain dump is tampered!!")

        return blockchain

    # ----------------------------------------- Not used yet ------------------------------------------------- #

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

    def print_transactions(self):
        print("--- Blockchain ---")
        for idx,block in enumerate(self.chain):
            print('\t--- Block %d (hash: %s)' % (idx, block.hash))
            for tx in block.transactions:
                print('\t\tid:%s, \t%d' % (tx.transaction_id[0:10], tx.amount))

    def __str__(self):
        ret = "\n---Blockchain(blocks:" + str(len(self.chain)) + ")---\n"
        for block in self.chain:
            ret += (str(block) + "\n")
        return ret
