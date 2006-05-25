#! /usr/bin/python
import sys
sys.path.append('../src')
from task import *
from project import Project
from client import Client
from runner import Runner
import os, time

def filter_cvs_update( text ):
	dont_start_interr = lambda line : not line or not line[0]=='?'
	result = filter(dont_start_interr, text.split('\n') )	
	return '\n'.join(result)

def pass_text(text):
	return text

start_time = -1
def start_timer(out):
	global start_time
	start_time = time.time()
def deployment_time(output):
	global start_time
	return {'deployment_time' : time.time() - start_time}
def exectime_functests(output):
	global start_time
	return {'exectime_functests' : time.time() - start_time}
	
clam = Task(
	project = Project("CLAM"),
	client = Client("testing-machine_osx-tiger"),
	task_name = "updating the cvs"
	)


clam.add_checking_for_new_commits( 
	checking_cmd="cd $HOME/clam-sandboxes/testing-clam && cvs -nq up  | grep ^[UP]",  
	minutes_idle=5
)

clam.add_subtask("Which new commits?", [	
	"cd $HOME/clam-sandboxes",
	{ CMD: "cd testing-clam && cvs -q up", INFO: filter_cvs_update },
] )
clam.add_deployment( [
	{INFO: start_timer},
	"cd $HOME/clam-sandboxes",
#	"cvs co -d testing-clam CLAM",
	"cd testing-clam",
	{CMD: "cvs up -dP", INFO: pass_text},
	"cd $HOME/clam-sandboxes/testing-clam/scons/libs",
	"scons configure",
	"scons",
	{INFO: deployment_time}
#	"sudo scons install",
] )

clam.add_subtask("SMSTools installation", [
	"cd $HOME/clam-sandboxes",
#	"cvs co -d testing-smstools CLAM_SMSTools",
	"cd testing-smstools && cvs up ",
	"cd $HOME/clam-sandboxes/testing-smstools/scons/QtSMSTools",
	"scons"
] )

clam.add_subtask("execute QTSMStools", [
	"cd $HOME/clam-sandboxes/testing-smstools/scons/QtSMSTools",
	"scons"
#	"./QtSMSTools"
] )

clam.add_subtask("NetworkEditor installation", [
	"cd $HOME/clam-sandboxes",
#	"cvs co -d testing-neteditor CLAM_NetworkEditor",
	"cd testing-neteditor && cvs up -dP",
	"cd scons",
	"scons"
] )

clam.add_subtask("execute NetworkEditor", [
	"cd $HOME/clam-sandboxes/testing-neteditor/scons",
#	"./NetworkEditor"
] )


Runner( 
	clam, 
	continuous=True,
	remote_server_url='http://10.55.0.66/testfarm_server',
)

