#! /usr/bin/python

from testfarmclient import * 


example = Repository("this_is_just_a_test")

example.add_deployment_task( [
	{CMD: "echo lalala", INFO: lambda x : x},
	{CMD: "ls", INFO: lambda x : x}
] )

#example.add_checking_for_new_commits( "cvs -nq up -dP | grep ^[UP]" )

example.add_task("teeesting", [
	#"./lalala fafaf",
	"echo Should not write this!"
] )
example.add_task("just a CD", [
	{CD:"/tmp"}
] )



if 1 :
	TestFarmClient( 
		"an_example_client", 
		example, 
		html_base_dir='./html-example', 
		logs_base_dir='/tmp/testfarm_example_logs',
		continuous=False 
	)

else :	
	TestFarmClient( 
		"pau_computer", 
		example, 
		remote_server_url="http://10.55.0.66/testfarm_server", #TODO check if url accessible, or responds
		continuous=False
	)

