from block import Block
#abd
def verify_transaction_main_branch(self, transaction):
    main_branch_utxos = []
    for tx_in in transaction.transaction_inputs:
        if tx_in.previous_output_id not in main_branch_utxos[transaction.sender_address]:
            print("Transaction rejected. tx_in '%s' not in utxos of sender" % tx_in.previous_output_id[0:20])
            return False
    return True


def add_to_wallet_if_mine(selft, transaction, wallet):
    if transaction.recipient_address == wallet.public_key:
        print("Receieved a transaction for ", transaction.amount)


def remove_matching_from_pool(self, transaction):
    transaction_pool = []

    for idx, pool_tx in enumerate(transaction_pool):
        if pool_tx.transaction_id == transaction.transaction_id:
            print("Removed transaction %d from pool" % idx)
            transaction_pool.remove(pool_tx)


def add_block_main_branch(self, block, wallet, blockchain):
    # blockchain = {}
    for transaction in block.transactions:
        if not self.verify_transaction_main_branch(transaction):
            return False
        self.add_to_wallet_if_mine(transaction, wallet)
        self.remove_matching_from_pool(transaction)
    self.broadcast_block_to_peers(block)
    blockchain[block.hash] = block


def add_block_side_branch(self, block, blockchain):
    blockchain[block.hash] = block

def add_block_side_branch_consensus(self, block, blockchain):
    current_mb_block = Block()
    fork_from_block = blockchain[block.previous_hash]
    if fork_from_block is None:
        print("[s_b_consensus]Error: previous hash not in chain")
    while current_mb_block.hash != fork_from_block.hash:
        blockchain.remove(current_mb_block)
        current_mb_block = blockchain[current_mb_block.previous_hash]
        if current_mb_block is None:
            print("[s_b_consensus]Error: previous hash not in chain (should never happen)...")
def received_block(block, blockchain, wallet, difficulty, main_branch, orhpan_blocks, current_mb_block):
    # 2) Reject if duplicate of block we have in any of the three categories
    if blockchain[block.hash] is not None:
        print("[received_block]Error: duplicate block")
        return False

    # 3)Transaction list must be non-empty
    if len(block.transactions) == 0:
        print("[received_block]Error: Empty transaction list")
        return False

    # 4)Block hash must satisfy claimed nBits proof of work
    if not block.hash.startswith('0' * difficulty):
        print("[received_block]Error: Blcok doesn't match current difficulty of %d" % difficulty)
        return False

    # 6)For each transaction, apply "tx" checks 2-4
    for transaction in block.transactions:
        pass

    # 7)Verify Merkle hash
    if not verify_merkle_hash(block):
        return False

    # 8) Check if prev block (matching prev hash) is in main branch
    # οr side branches.
    if blockchain[block.previous_hash] is None:
        # If not, add this to orphan blocks, then query
        # peer we got this from for 1st missing orphan block in prev chain;
        # done with block
        blockchain[block.hash] = block
        return True

    prev_block = blockchain[block.previous_hash]
    # 16) For case 1, adding to main branch:
    if prev_block.main_branch == 0:
        # 16) For case 1, adding to main branch:
        for transaction in block.transactions:
            if not process_mb_transaction(transaction):
                return False
            add_to_wallet_if_mine(transaction, wallet)
            remove_matching_from_pool(transaction)
        broadcast_block_to_peers(block)
        block.main_branch = 0
        blockchain[block.hash] = block
    elif prev_block.main_branch == 1:

        if prev_block.chain_length > current_mb_block.chain_length:
            # 18) For case 3, a side branch becoming the main branch:

            # 19) Find the fork block on the main branch which this side branch forks off of
            temp_block = prev_block
            while temp_block.main_branch == 1:
                # 20) Redefine the main branch to only go up to this fork block
                temp_block.main_branch = 0
                temp_block = blockchain[prev_block.previous_hash]
            # The fork begins at this block
            # 21) For each block on the side branch, from the child of the fork block to the leaf, add to the main branch:
            while temp_block.
        else:
            # 17) For case 2, adding to a side branch, we don't do anything.
            block.main_branch = 1
            blockchain[block.hash] = block




