import threading

node = ""
numOfClients = 5
bootstrapIp = "http://127.0.0.1:22147"
flag_lock = threading.Lock()
add_block_lock = threading.Lock()
add_transaction = threading.Lock()
seq_mining_lock = threading.Lock()
reading_writing_blockchain = threading.Lock()
peers_ids = dict()


