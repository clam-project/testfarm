#! /usr/bin/python

import sys
sys.path.append('../src')
from task import *
from project import Project
from client import Client
from runner import Runner
import os, time

start_time = -1
def start_timer(output):
	global start_time
	start_time = time.time()
def exectime_unittests(output):
	global start_time
	return {'exectime_unittests' : time.time() - start_time}
def exectime_functests(output):
	global start_time
	return {'exectime_functests' : time.time() - start_time}


HOME = os.environ['HOME']
os.environ['LD_LIBRARY_PATH']='%s/clam-sandboxes/tlocal/lib:/usr/local/lib' % HOME

def filter_cvs_update( text ):
	dont_start_interr = lambda line : not line or not line[0]=='?'
	result = filter(dont_start_interr, text.split('\n') )	
	return '\n'.join(result)



clam = Task(
	project = Project("CLAM"), 
	client = Client("testing_machine-linux_breezy"), 
	task_name="with cvs update" 
	)

clam.add_checking_for_new_commits( 
	checking_cmd="cd $HOME/clam-sandboxes/testing-clam && cvs -nq up -dP | grep ^[UP]",  
	minutes_idle=5
)
clam.add_deployment( [
	"cd $HOME/clam-sandboxes",
	"cvs co -d testing-clam CLAM",
#	{ CMD: "cd testing-clam && cvs -q up -dP", INFO: filter_cvs_update },
	"cd $HOME/clam-sandboxes/testing-clam/scons/libs",
	"scons configure prefix=$HOME/clam-sandboxes/tlocal",
	"scons install",
	"scons install",
] )
clam.add_subtask("SMSTools installation", [
	"cd $HOME/clam-sandboxes",
	"cvs co -d testing-smstools CLAM_SMSTools",
#	"cd testing-smstools && cvs up -dP",
	"cd $HOME/clam-sandboxes/testing-smstools/scons/QtSMSTools",
	"scons clam_prefix=$HOME/clam-sandboxes/tlocal"
] )
'''
clam.add_subtask("execute QTSMStools", [
	"cd $HOME/clam-sandboxes/testing-smstools/scons/QtSMSTools",
	"./QtSMSTools" #TODO run a while
] )
'''
clam.add_subtask("NetworkEditor installation", [
	"cd $HOME/clam-sandboxes",
#	"cvs co -d testing-neteditor CLAM_NetworkEditor",
	"cd testing-neteditor && cvs up -dP",
	"cd scons",
	"scons clam_prefix=$HOME/clam-sandboxes/tlocal"
] )
'''
clam.add_subtask("execute NetworkEditor", [
	"cd $HOME/clam-sandboxes/testing-neteditor/scons",
	"./NetworkEditor" #TODO run a while
] )
'''
clam.add_subtask("Deploy OLD (srcdeps) build system", [
	"cd $HOME/clam-sandboxes/testing-clam/build/srcdeps",
	"make",
	"cd ..",
	"pwd && autoconf",
	"./configure"
	
])
clam.add_subtask("Unit Tests (with srcdeps)", [
	"cd $HOME/clam-sandboxes/testing-clam",
	"cd build/Tests/UnitTests",
	"make depend",
	"CONFIG=release make",
	{INFO : start_timer}, 
	{CMD:"./UnitTests", INFO: lambda x : x},
	{STATS : exectime_unittests}

] )
clam.add_subtask("Functional Tests (with srcdeps)", [
	"cd $HOME/clam-sandboxes/testing-clam",
	"cd build/Tests/FunctionalTests",
	"make depend",
	"CONFIG=release make",
	{INFO : start_timer}, 
	{CMD:"./FunctionalTests", INFO: lambda x : x},
	{STATS : exectime_functests}
] )

clam.add_subtask("Deploy SMSTools srcdeps branch for SMSBase tests", [
	"cd $HOME/clam-sandboxes",
	"rm -rf testing-smstools-srcdeps",
	"cvs co -r srcdeps-build-system-branch -d testing-smstools-srcdeps CLAM_SMSTools",
	'echo "CLAM_PATH=$HOME/clam-sandboxes/testing-clam/" > testing-smstools-srcdeps/build/clam-location.cfg'
] )
'''
clam.add_subtask("Testing SMSTransformations (using SMSTools srcdeps branch)", [
	"cd $HOME/clam-sandboxes",
	"cd testing-smstools-srcdeps/build/FunctionalTests",
	"make depend",
	"CONFIG=debug make", #release doesn't work
	{CMD: "./SMSToolsTests", INFO: lambda x : x}
] )
'''
Runner( clam, 
	continuous = True,
	remote_server_url = 'http://10.55.0.66/testfarm_server'
)

