#! /usr/bin/python

from testfarm import Repository, TestsFarmClient

clam = Repository("CLAM")
clam.add_deployment_task( [
	"cvs co -d testing-clam CLAM",
	"cd testing-clam/scons/libs",
	"scons configure prefix=/tmp",
	"scons install",

	"cvs co -d testing-smstools CLAM_SMSTools",
	"cd testing-smstools/scons/QtSMSTools",
	"scons clam_prefix=/tmp"
] )
clam.add_task("execute QTSMStools", [
	"cd testing-smstools/scons/QtSMSTools",
	"./QtSMSTools"
] )



TestsFarmClient( [
	clam
] )
