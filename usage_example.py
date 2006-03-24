#! /usr/bin/python

from testfarmclient import * 


example = Repository("Example")

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


'''
TestFarmClient( 
	"an_example_client", 
	[example ], 
	generated_html_path='./html-example', 
	logs_path='/tmp/testfarm_example_logs',
	continuous=false 
)
'''
	
from serverlistenerproxy import ServerListenerProxy

TestFarmClient( 
	"davids_computer", 
	[example ], 
	listeners = [ServerListenerProxy()],
	remote_server_url="http://10.55.0.66/testfarm_server",
	continuous=False
)

