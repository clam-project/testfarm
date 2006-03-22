#! /usr/bin/python

from testfarmclient import *

clam = Repository("CLAM")
clam.add_task("starting clam", ["echo foo"])

clam.add_checking_for_new_commits( 
	checking_cmd="cd $HOME/clam-sandboxes/testing-clam && cvs -nq up -dP | grep ^[UP]",  
	minutes_idle=0.2
)

clam.add_deployment_task( [
	"cd $HOME/clam-sandboxes",
	"cvs co -d testing-clam CLAM",
	"cvs co -d testing-smstools CLAM_SMSTools",
	"cd $HOME/clam-sandboxes/testing-clam/scons/libs",
	"scons configure prefix=/tmp",
	"scons install",

	"cd $HOME/clam-sandboxes",
	"cvs co -d testing-smstools CLAM_SMSTools",
	"cd testing-smstools/scons/QtSMSTools",
	"scons clam_prefix=/tmp"
] )
clam.add_task("execute QTSMStools", [
	"cd $HOME/clam-sandboxes/testing-smstools/scons/QtSMSTools",
	"./QtSMSTools"
] )


TestFarmClient( "pau_linux_breezy", [clam ], use_pushing_server=True, continuous=False )

