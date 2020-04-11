#!/usr/bin/python3

import sys
import os
import subprocess

if len(sys.argv) != 2:
    print("usage: count_tx <tx_file>")
    sys.exit()

tx_file = sys.argv[1]
print('node_id\t\tunder 10\tover10\t\tsum')
res = {}
for node_id in ["id0", "id1", "id2", "id3", "id4"]:
    cmd = '{if ($1 == "%s" && $2 <= 10) {n+=$2}} END{print(n)}' % node_id
    res[0] = subprocess.run(['awk', cmd, tx_file], stdout=subprocess.PIPE).stdout.decode('utf-8')
    
    #kati = subprocess.run(['awk', cmd, tx_file], stdout=subprocess.PIPE).stdout.decode('utf-8')
    #print(kati)
    #print(res[0].strip())
    cmd = '{if ($1 == "%s" && $2 > 10) {n+=$2}} END{print(n)}' % node_id
    res[1] = subprocess.run(['awk', cmd, tx_file], stdout=subprocess.PIPE).stdout.decode('utf-8')

    cmd = '{if ($1 == "%s") {n+=$2}} END{print(n)}' % node_id
    res[2] = subprocess.run(['awk', cmd, tx_file], stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(node_id + ':', end='')
    for r in res:
        print('\t\t' + str(res[r].strip()), end='')
    print('')



