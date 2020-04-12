
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

        # print(self)
        # Return the updated dict_nodes_utxos_by_block_id to node
        # return self.dict_nodes_utxos_by_block_id
