#! /usr/bin/python

import sys
sys.path.append('../src')
from task import *
from runner import Runner 

example = Task(	project_name = "example project",
		client_name = "an_example_client",
		task_name = "this_is_just_a_test"
)

example.add_deployment( [
	{CMD: "echo lalala", INFO: lambda x : x},
	{CMD: "ls", INFO: lambda x : x}
] )

#example.add_checking_for_new_commits( "cvs -nq up -dP | grep ^[UP]" )

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



