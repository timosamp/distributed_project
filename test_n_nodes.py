#!/usr/bin/env python3
import os
import signal
import subprocess
import sys
from subprocess import Popen, PIPE
from time import sleep


def main():
    # Opens n (arg1) terminals with client.py
    if len(sys.argv) != 2:
        print("Invalid number of arguments.\nUsage: test_n_nodes.py <n>")
        return
    n = int(sys.argv[1])
    port = 22147

    proc0 = Popen(['gnome-terminal', '--', 'python3', 'client.py', '-b'], stdin=PIPE, preexec_fn=os.setpgrp())
    sleep(1)
    proc = {}
    for i in range(1,n):
        port_option = port+i
        proc[i] = Popen('gnome-terminal -- python3 client.py -p %d' % port_option, stdin=PIPE, shell=True, preexec_fn=os.setpgrp())
        sleep(1)

    c = proc0.pid
    print(c)
    c1  = proc[1].pid
    print(c1)
    proc0.stdin.write(bytes('tff 5nodes/transactions0.txt', 'ascii'))


    print('node0 says: ')
    proc0.stdin.write(bytes('t id1 5', 'ascii'))
    print('node0 says: %s')
    sleep(2)
    out, err = proc[1].communicate(bytes('t id1 5', 'ascii'))
    print('node1 says: %s', out)

    input("press key to close threads")
    os.killpg(os.getpgid(proc0.pid), signal.SIGTERM)  # Send the signal to all the process groups
    proc0.wait()
    for i in range(1,n):
        proc[i].wait()

main()