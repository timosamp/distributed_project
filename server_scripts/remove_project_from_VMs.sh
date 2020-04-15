#!/bin/bash

set +e

ssh -t user@snf-12498.ok-kno.grnetcloud.net "\
			rm -r last_codes/; \
			ssh -t user@192.168.0.2 \" rm -r last_codes/; \"; \
			ssh -t user@192.168.0.3 \" rm -r last_codes/; \"; \
			ssh -t user@192.168.0.4 \" rm -r last_codes/; \"; \
			ssh -t user@192.168.0.5 \" rm -r last_codes/; \";" 

