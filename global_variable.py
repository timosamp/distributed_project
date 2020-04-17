import threading

node = ""
numOfClients = 10
# bootstrapIp = "http://127.0.0.1:22147"
bootstrapIp = "http://192.168.0.1:22147" # -- for server
sendCoinsTo_lock = threading.Lock()
flag_lock = threading.Lock()
add_block_lock = threading.Lock()
add_transaction = threading.Lock()
seq_mining_lock = threading.Lock()
reading_writing_blockchain = threading.Lock()
peers_ids = dict()


