#! /usr/bin/python

import sys
sys.path.append('../src')
from task import *
from runner import Runner 
from project import Project
from client import Client
from runner import Runner
from commands import getoutput

example = Task(	project = Project("example project"),
		client = Client("an_example_client"),
		task_name = "this_is_just_a_test"
)

example.add_deployment( [
	{CMD: "echo lalala", INFO: lambda x : x},
	{CMD: "ls", INFO: lambda x : x}
] )

#example.set_check_for_new_commits( "cvs -nq up -dP | grep ^[UP]" )

example.add_subtask("teeesting", [
	"echo Should not write this!"
] )
example.add_subtask("just a CD", ["cd /tmp"] )

local = True

if local :
	Runner( example,
		continuous = False,
		local_base_dir = 'local_dir'
	)

else :	

	Runner( example,
		remote_server_url="http://10.55.0.66/testfarm_server",
		continuous=False
	)



