import json

import jsonpickle
import requests

from block import Block
# abd
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

    return True

def process_transaction_main_branch(transaction):
    # 1) For each input, look in the main branch to find the referenced output transaction. Reject if the output transaction is missing for any input.

    # 2) For each input, if we are using the nth output of the earlier transaction, but it has fewer than n+1 outputs, reject.

    # 3) Verify crypto signatures for each input; reject if any are bad

    # 4) For each input, if the referenced output has already been spent by a transaction in the main branch, reject

    # 5) Using the referenced output transactions to get input values, check that each input value, as well as the sum, are in legal money range

    # 6) Reject if the sum of input values < sum of output values
    pass

def receive_transaction(transaction):

    """
    # 1) Check syntactic correctness

    # 2) Make sure neither in or out lists are empty

    # ((Size in bytes <= MAX_BLOCK_SIZE))
    # ((Each output value, as well as the total, must be in legal money range))
    # ((Reject "nonstandard" transactions: scriptSig doing anything other than pushing
    #  numbers on the stack, or scriptPubkey not matching the two usual forms[4]))

    # 3) Reject if we already have matching tx in the pool, or in a block in the main branch

    # 4) For each input, if the referenced output exists in any other tx in the pool, reject this transaction.[5]

    # 5) For each input, look in the main branch and the transaction pool
    #  to find the referenced output transaction. If the output transaction
    #  is missing for any input, this will be an orphan transaction. Add to
    #  the orphan transactions, if a matching transaction is not in there already.

    # 6) For each input, if the referenced output does not exist (e.g. never
    #  existed or has already been spent), reject this transaction[6]

    # ((Using the referenced output transactions to get input values, check that
    #   each input value, as well as the sum, are in legal money range))

    # 7) Reject if the sum of input values < sum of output values

    # 8) Verify the scriptPubKey accepts for each input; reject if any are bad

    # 9) Add to transaction pool[7]

    # 10) "Add to wallet if mine"

    # 11) Relay transaction to peers

    # 12) For each orphan transaction that uses this one as one of its inputs, run all these steps (including this one) recursively on that orphan"""


def check_block(block, difficulty):
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

    return True


def received_block(block, blockchain, wallet, difficulty, main_branch, orhpan_blocks, current_mb_block):
    # 2) Reject if duplicate of block we have in any of the three categories
    if blockchain[block.hash] is not None:
        print("[received_block]Error: duplicate block")
        return False

    # Do 3) - 11) checks
    if not check_block(block, difficulty):
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
        add_block_main_branch(block, wallet, blockchain)
    elif prev_block.main_branch == 1:
        if prev_block.chain_length > current_mb_block.chain_length:
            add_block_side_branch_consensus(block, blockchain, difficulty)
        else:
            add_block_side_branch(block, blockchain)

    return True


def add_block_main_branch(self, block, wallet, blockchain):
    # 16) For case 1, adding to main branch:
    for transaction in block.transactions:
        if not process_mb_transaction(transaction):
            return False
        add_to_wallet_if_mine(transaction, wallet)
        remove_matching_from_pool(transaction)
    broadcast_block_to_peers(block)
    block.main_branch = 0
    blockchain[block.hash] = block


def add_block_side_branch_consensus(self, block, blockchain, difficulty, current_mb_block, transaction_pool, peers):
    #### For case 3, a side branch becoming the main branch #####

    # 1) Find the fork block on the main branch which this side branch forks off of
    temp_block = blockchain[block.previous_hash]
    while temp_block.main_branch == 1:
        # 2) Redefine the main branch to only go up to this fork block
        temp_block.main_branch = 0
        temp_block = blockchain[temp_block.previous_hash]

    # 3) For each block on the side branch, from the child of the fork block to the leaf, add to the main branch:
    fork_from_block = temp_block
    temp_block = blockchain[temp_block.next_hash]  # child of fork block
    rejected = False
    while temp_block.next_hash is not None:
        # 3.1) Do "branch" checks 3-11
        check_block(temp_block, difficulty)

        # 3.2) For all but the coinbase transaction, apply the following:
        for transaction in block:
            if not process_mb_transaction(transaction):
                # 4) If we reject at any point, leave the main branch as what it was originally, done with block
                return False
        # 3.3) For each transaction, "Add to wallet if mine"
        for transaction in block:
            add_to_wallet_if_mine(transaction)

    temp_block = current_mb_block
    # 5) For each block in the old main branch, from the leaf down to the child of the fork block:
    while temp_block.hash != fork_from_block.hash:
        # 5.1) For each non-coinbase transaction in the block:
        for transaction in temp_block:
            # 5.1.1) Apply "tx" checks 2-9, except in step 8,
            #only look in the transaction pool for duplicates, not the main branch
            pass
            # 5.1.2) Add to transaction pool if accepted, else go on to next transaction
            transaction_pool[transaction.transaction_id] = transaction
    # 6) For each block in the new main branch, from the child of the fork node to the leaf:
    # traverse the treee...
        # 6.1) For each transaction in the block, delete any matching transaction from the transaction pool

    # 7) Relay block to our peers
    broadcast_block_to_peers(block, peers)

    # 8) For each orphan block for which this block is its prev,
    # run all these steps (including this one) recursively on that orphan

def add_block_side_branch(self, block, blockchain):
    block.main_branch = 1
    blockchain[block.hash] = block
    return


def broadcast_block_to_peers(block, peers):
    cntr = 0
    # print("Broadcasting block to peers")
    for (idx, (peer, peer_url)) in enumerate(list(reversed(peers))):

        block_json = jsonpickle.encode(block)
        data = {"block": block_json}
        headers = {'Content-Type': "application/json"}
        url = "{}/add_block".format(peer_url)

        # print("Broadcast to: " + peer_url)

        r = requests.post(url,
                          data=json.dumps(data),
                          headers=headers)
        if r.status_code == 200:
            # print("Broadcast to peer ", idx, " success!")
            # break # consesus -- fixme: after testing
            cntr += 1
            x = 1
        else:
            x = 1
            print("Error: broadcast to peer ", idx)
    if cntr == len(peers):
        print("Broadcasted block to all peers")
    else:
        print("Error broadcasting block.")
