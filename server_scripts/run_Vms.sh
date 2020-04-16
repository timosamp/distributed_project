#!/bin/bash


set +e

gnome-terminal --geometry 80x20+400+200 -- ssh -t user@snf-12498.ok-kno.grnetcloud.net "\
			cd last_codes/;
			python3 client.py -b; bash -l"	

sleep 5


gnome-terminal --geometry 80x20+0+0 -- ssh -t user@snf-12498.ok-kno.grnetcloud.net "\
	  		ssh -t user@192.168.0.2 \"\
			cd last_codes/;
			python3 client.py -p 22148; bash -l\" "	

gnome-terminal --geometry 80x20+0+500 -- ssh -t user@snf-12498.ok-kno.grnetcloud.net "\
	  		ssh -t user@192.168.0.3 \"\
			cd last_codes/;
			python3 client.py -p 22149; bash -l\" "	

gnome-terminal --geometry 80x20+800+500 -- ssh -t user@snf-12498.ok-kno.grnetcloud.net "\
	  		ssh -t user@192.168.0.4 \"\
			cd last_codes/;
			python3 client.py -p 22150; bash -l\" "	

gnome-terminal --geometry 80x20+800+0 -- ssh -t user@snf-12498.ok-kno.grnetcloud.net "\
	  		ssh -t user@192.168.0.5 \"\
			cd last_codes/;
			python3 client.py -p 22151; bash -l\" "	

