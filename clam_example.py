#! /usr/bin/python

from testfarmclient import Repository, TestFarmClient

clam = Repository("CLAM")
clam.add_deployment_task( [
	"cd /home/parumi/clam-sandboxes",
	"cvs co -d testing-clam CLAM",
	"cd /home/parumi/clam-sandboxes/testing-clam/scons/libs",
	"scons configure prefix=/tmp",
	"scons install",

	"cd /home/parumi/clam-sandboxes",
	"cvs co -d testing-smstools CLAM_SMSTools",
	"cd testing-smstools/scons/QtSMSTools",
	"scons clam_prefix=/tmp"
] )
clam.add_task("execute QTSMStools", [
	"cd /home/parumi/clam-sandboxes/testing-smstools/scons/QtSMSTools",
	"./QtSMSTools"
] )



TestFarmClient( [
	clam
] )
