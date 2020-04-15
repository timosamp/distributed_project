# !/usr/bin/python3
import re
import sys
import os
import subprocess

initial_balance = 100

def main():
    if len(sys.argv) != 2:
        print("usage: count_tx <tx_file> OR count_tx <num_of_nodes>")
        sys.exit()
    if sys.argv[1].isdecimal():
        count_final_balances(int(sys.argv[1]))
        return
    tx_file = sys.argv[1]

    #get number of node from transactions file
    node_num = int(re.sub("[^0-9]", "", tx_file))
    print('node_id\t\tunder 10\tover10\t\tsum')

    count_tx_py_n(tx_file, 5)



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
    return res

def count_final_balances(n):
    global initial_balance
    dirname = ''
    if n <= 5:
        dirname = '5nodes'
    else:
        dirname = '10nodes'
    sent_txs_u10 = {}
    final_balances = {}

    for sender_node in range (0,n):
        final_balances[sender_node] = initial_balance
        filename = '/backup/transactions%d.txt' % sender_node
        # filename = '/transactions%d.txt' % sender_node
        sent_txs = count_tx_py_n(dirname + filename, n)
        #sent_txs_u10[sender_node] = sent_txs[:][0]
        sent_txs_u10[sender_node] = sent_txs

    #print(sent_txs_u10)
    #print(sent_txs_u10.values())
    for receiver_node in range(0,n):
        final_balances[receiver_node] -= sum(sent_txs_u10[receiver_node][i] for i in range (0,n))

        #final_balances[receiver_node] -= sum(sent_txs_u10[receiver_node].values())
        final_balances[receiver_node] += sum(list(sent_txs_u10[i][receiver_node] for i in range(0,n)))
        #final_balances[receiver_node] += sum(sent_txs_u10[:][receiver_node])

    print(final_balances)

def count_tx_py_n(tx_file, n):
    res_ue10 = {}
    res_o10 = {}
    res_tot = {}

    for node_num in range(0,10):
        res_ue10[node_num] = 0
        res_o10[node_num] = 0
        res_tot[node_num] = 0

    print(tx_file)
    f = open(tx_file, "r")
    for line in f:
        s = line.split(' ')
        #strip a string from all non-numeric characters
        node_num = int(re.sub("[^0-9]", "", s[0]))
        if (int(s[1]) <= 15):
            res_ue10[node_num] += int(s[1])
        else:
            res_o10[node_num] += int(s[1])
        res_tot[node_num] += int(s[1])

    # for node_num in range(0,n):
    #     print(str(node_num) + ':', end='')
    #     for r in [0,1,2]:
    #         print('\t\t' + str(res[node_num][r]), end='')
    #     print('')
    f.close()
    print('res_ue10:')
    for i in {i : res_ue10[i] for i in range(0,n)}:
        print('node %d: %d' % (i, res_ue10[i]))

    return res_ue10

main()