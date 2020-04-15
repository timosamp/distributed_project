#!/bin/bash


set +e

gnome-terminal --geometry 80x20+400+200 -- ssh -t user@snf-12498.ok-kno.grnetcloud.net 


gnome-terminal --geometry 80x20+0+0 -- ssh -t user@snf-12498.ok-kno.grnetcloud.net "\
	  		ssh -t user@192.168.0.2 \"\
				hostname; bash -l\"; "

gnome-terminal --geometry 80x20+0+500 -- ssh -t user@snf-12498.ok-kno.grnetcloud.net "\
	  		ssh -t user@192.168.0.3 \"\
				hostname; bash -l\"; "

gnome-terminal --geometry 80x20+800+500 -- ssh -t user@snf-12498.ok-kno.grnetcloud.net "\
	  		ssh -t user@192.168.0.4 \"\
				hostname; bash -l\"; "

gnome-terminal --geometry 80x20+800+0 -- ssh -t user@snf-12498.ok-kno.grnetcloud.net "\
	  		ssh -t user@192.168.0.5 \"\
				hostname; bash -l\"; "

