#!/bin/bash
set -e 
#gnome-terminal -- 'python3 client.py -b'
gnome-terminal -- bash -c "python3 client.py -b;exec bash"
sleep 1
gnome-terminal -- bash -c "python3 client.py -p 22148;exec bash" 