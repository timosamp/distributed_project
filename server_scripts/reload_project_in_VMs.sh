#!/bin/bash


set +e

./copy_files_from_project_dir.sh
./remove_project_from_VMs.sh
./load_project_to_VMs.sh
ssh user@snf-12498.ok-kno.grnetcloud.net
