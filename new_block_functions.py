from block import Block

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


