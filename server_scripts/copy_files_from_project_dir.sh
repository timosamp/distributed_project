#!/bin/bash


set +e

cp ../working_dir/distributed_project/*.py ./distributed_project_vm_load/
cp ../working_dir/distributed_project/*.sh ./distributed_project_vm_load/
cp -r ../working_dir/distributed_project/5nodes ./distributed_project_vm_load/
cp -r ../working_dir/distributed_project/10nodes ./distributed_project_vm_load/
cp -r ../working_dir/distributed_project/result ./distributed_project_vm_load/
cp -r ../working_dir/distributed_project/logs ./distributed_project_vm_load/
