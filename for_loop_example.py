#! /usr/bin/python

from testfarmclient import Repository, TestFarmClient
from test_testsfarmserver import TestFarmServer

for_loop = Repository("FOR LOOP")

for_loop.add_task("compile and execute for loop", [
	"cd for_loop_example",
	"gcc for_loop.c -o for_loop",
	"./for_loop"
] )



TestFarmClient( [
	for_loop
], [TestFarmServer()] )
