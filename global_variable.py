import threading

node = ""
numOfClients = 2
bootstrapIp = "http://127.0.0.1:22147"
flag_lock = threading.Lock()
add_block_lock = threading.Lock()
add_transaction = threading.Lock()

