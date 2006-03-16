#! /usr/bin/python

from testfarm import Repository, TestsFarmClient
from test_testsfarmserver import TestsFarmServer

for_loop = Repository("FOR LOOP")

for_loop.add_task("compile and execute for loop", [
	"cd for_loop_example",
	"gcc for_loop.c -o for_loop",
	"./for_loop"
] )



TestsFarmClient( [
	for_loop
], [TestsFarmServer()] )
