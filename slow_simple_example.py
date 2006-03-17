#! /usr/bin/python

from testfarmclient import Repository, TestFarmClient

for_loop = Repository("slow test")

for_loop.add_task("echo", ["echo hello"] )
for_loop.add_task("sleep 5 seconds", ["sleep 5"] )
for_loop.add_task("sleep 3 seconds", ["sleep 3"] )



TestFarmClient( [for_loop], use_pushing_server=True )
