#!/bin/bash
set -e 
#gnome-terminal -- 'python3 client.py -b'
gnome-terminal --geometry 80x20+400+200 -- bash -c "python3 client.py -b -test1;exec bash"
sleep 1
gnome-terminal --geometry 80x20+0+0 -- bash -c "python3 client.py -p 22148 -test1;exec bash"
sleep 1
gnome-terminal --geometry 80x20+0+400 -- bash -c "python3 client.py -p 22149 -test1;exec bash"
sleep 1
gnome-terminal --geometry 80x20+800+400 -- bash -c "python3 client.py -p 22150 -test1;exec bash"
sleep 1
gnome-terminal --geometry 80x20+800+0 -- bash -c "python3 client.py -p 22151 -test1;exec bash"
