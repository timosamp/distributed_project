#!/bin/bash

set +e

scp -r /media/ritos/Data/sxoli/Y/distributed/project/codes/0_for_cloud/distributed_project_vm_load user@snf-12498.ok-kno.grnetcloud.net:/home/user/last_codes/

sleep 2 

ssh -t user@snf-12498.ok-kno.grnetcloud.net "\
	scp -r /home/user/last_codes/ user@192.168.0.2:/home/user/last_codes/; \
        scp -r /home/user/last_codes/ user@192.168.0.3:/home/user/last_codes/; \
        scp -r /home/user/last_codes/ user@192.168.0.4:/home/user/last_codes/; \
        scp -r /home/user/last_codes/ user@192.168.0.5:/home/user/last_codes/; "


