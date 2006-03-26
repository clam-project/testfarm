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



if 0 :
	TestFarmClient( 
		"an_example_client", 
		example, 
		generated_html_path='./html-example', 
		logs_path='/tmp/testfarm_example_logs',
		continuous=False 
	)

else :	
	TestFarmClient( 
		"pau_computer", 
		example, 
		#remote_server_url="http://10.55.0.66/testfarm_server", #TODO check if url accessible, or responds
		remote_server_url="http://localhost/testfarm_server",
		continuous=False
	)

