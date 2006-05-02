#! /usr/bin/python
import sys
sys.path.append('../src')
from testfarmclient import *
import os

def filter_cvs_update( text ):
	dont_start_interr = lambda line : not line or not line[0]=='?'
	result = filter(dont_start_interr, text.split('\n') )	
	return '\n'.join(result)

def pass_text(text):
	return text

clam = Repository("CLAM")
clam.add_task("starting clam", ["cd .. && cd testfarm && echo foo && pwd"])
'''
clam.add_checking_for_new_commits( 
	checking_cmd="cd $HOME/clam-sandboxes/testing-clam && cvs -nq up  | grep ^[UP]",  
	minutes_idle=5
)

clam.add_task("Which new commits?", [	
	"cd $HOME/clam-sandboxes",
	{ CMD: "cd testing-clam && cvs -q up", INFO: filter_cvs_update },
] )
'''
clam.add_deployment_task( [
	"cd $HOME/clam-sandboxes",
#	"cvs co -d testing-clam CLAM",
	"cd testing-clam",
	{CMD: "cvs up -dP", INFO: pass_text},
	"cd $HOME/clam-sandboxes/testing-clam/scons/libs",
	"scons configure",
	"scons",
#	"sudo scons install",
] )

clam.add_task("SMSTools installation", [
	"cd $HOME/clam-sandboxes",
#	"cvs co -d testing-smstools CLAM_SMSTools",
	"cd testing-smstools && cvs up ",
	"cd $HOME/clam-sandboxes/testing-smstools/scons/QtSMSTools",
	"scons"
] )

clam.add_task("execute QTSMStools", [
	"cd $HOME/clam-sandboxes/testing-smstools/scons/QtSMSTools",
	"scons"
#	"./QtSMSTools"
] )

clam.add_task("NetworkEditor installation", [
	"cd $HOME/clam-sandboxes",
#	"cvs co -d testing-neteditor CLAM_NetworkEditor",
	"cd testing-neteditor && cvs up -dP",
	"cd scons",
	"scons"
] )

clam.add_task("execute NetworkEditor", [
	"cd $HOME/clam-sandboxes/testing-neteditor/scons",
#	"./NetworkEditor"
] )


TestFarmClient( 
	"testing-machine_osx-tiger", 
	clam, 
	remote_server_url='http://10.55.0.66/testfarm_server',
	continuous=True,
	verbose=True
)

