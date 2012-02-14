#! /bin/bash

while [ 1 ]; do
	./run_remote_server_once.py
	echo Sleeping some minutes
	sleep 300
done

