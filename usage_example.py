#! /usr/bin/python

from testfarmclient import * 

clam = Repository("CLAM")

clam.add_deployment_task( [
	"echo lalala",
	"ls" 
] )

#clam.add_checking_for_new_commits( "cvs -nq up -dP | grep ^[UP]" )

clam.add_task("teeesting", [
	#"./lalala fafaf",
	"echo Should not write this!"
] )
clam.add_task("just a CD", [
	{CD:"/tmp"}
] )


TestFarmClient( "pau_linux_breezy", [clam], use_pushing_server=True)

TestFarmClient( "another_computer", [clam], use_pushing_server=True)
