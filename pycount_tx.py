# !/usr/bin/python3

import sys
import os
import subprocess


def main():
    if len(sys.argv) != 2:
        print("usage: count_tx <tx_file>")
        sys.exit()

    tx_file = sys.argv[1]
    print('node_id\t\tunder 10\tover10\t\tsum')
    count_tx_py(tx_file)



def balances_with_awk(tx_file):
    res = {}
    for node_id in ["id0", "id1", "id2", "id3", "id4"]:
        cmd = '{if ($1 == "%s" && $2 <= 10) {n+=$2}} END{print(n)}' % node_id
        res[0] = subprocess.run(['awk', cmd, tx_file], stdout=subprocess.PIPE).stdout.decode('utf-8')

        # kati = subprocess.run(['awk', cmd, tx_file], stdout=subprocess.PIPE).stdout.decode('utf-8')
        # print(kati)
        # print(res[0].strip())
        cmd = '{if ($1 == "%s" && $2 > 10) {n+=$2}} END{print(n)}' % node_id
        res[1] = subprocess.run(['awk', cmd, tx_file], stdout=subprocess.PIPE).stdout.decode('utf-8')

        cmd = '{if ($1 == "%s") {n+=$2}} END{print(n)}' % node_id
        res[2] = subprocess.run(['awk', cmd, tx_file], stdout=subprocess.PIPE).stdout.decode('utf-8')
        print(node_id + ':', end='')
        for r in res:
            print('\t\t' + str(res[r].strip()), end='')
        print('')


def count_tx_py(tx_file):
    res = {}
    for id in ["id0", "id1", "id2", "id3", "id4"]:
        res[id] = {}
        res[id][0] = 0
        res[id][1] = 0
        res[id][2] = 0

    f = open(tx_file, "r")
    for line in f:
        s = line.split(' ')
        if (int(s[1]) <= 15):
            res[s[0]][0] += int(s[1])
        else:
            res[s[0]][1] += int(s[1])
        res[s[0]][2] += int(s[1])

    for id in ["id0", "id1", "id2", "id3", "id4"]:
        print(id + ':', end='')
        for r in [0,1,2]:
            print('\t\t' + str(res[id][r]), end='')
        print('')
    f.close()

main()