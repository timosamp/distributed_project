# !/usr/bin/python3

import sys
import os
import subprocess


def main():

    tx_files = ["5nodes/transactions0.txt", "5nodes/transactions1.txt",
                "5nodes/transactions2.txt", "5nodes/transactions3.txt", "5nodes/transactions4.txt"]

    dict_nodes = dict()

    # Init
    for idx, tx_file in enumerate(tx_files):
        dict_nodes["id" + str(idx)] = 100

    # How money have they got in the end?
    for idx, tx_file in enumerate(tx_files):
        res_dict = count_tx_py(tx_file, idx)
        for node_id in res_dict:
            dict_nodes[node_id] += res_dict[node_id]

    # Print the results
    for node_id in dict_nodes:
        print("node_" + node_id + " has " + str(dict_nodes[node_id]))




def count_tx_py(tx_file, idx):
    res = {}
    for node_id in ["id0", "id1", "id2", "id3", "id4"]:
        res[node_id] = dict()
        res[node_id] = 0

    f = open(tx_file, "r")
    for line in f:
        s = line.split(' ')
        if int(s[1]) <= 15:
            # Add the money to the receiver
            res[s[0]] += int(s[1])
            # Remove them form the sender
            res["id" + str(idx)] -= int(s[1])

    f.close()
    return res

main()