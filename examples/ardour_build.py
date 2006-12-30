#! /usr/bin/python

import sys
sys.path.append('../src')
from task import *
from project import Project
from client import Client
from runner import Runner
import os, time

startTime = -1
def startTimer():
	global startTime
	startTime = time.time()
def ellapsedTime():
	global startTime
	return time.time() - startTime

HOME = os.environ['HOME']
os.environ['LD_LIBRARY_PATH']='%s/src/tlocal/lib:/usr/local/lib' % HOME
os.environ['LANG']=''

client = Client("linux_ubuntu_edgy")
client.brief_description = '<img src="http://clam.iua.upf.es/images/linux_icon.png"/> <img src="http://clam.iua.upf.es/images/ubuntu_icon.png"/>'
	

clam = Task(
	project = Project("ardour2-trunk"), 
	client = client, 
	task_name="with svn update" 
	)

clam.set_check_for_new_commits( 
		checking_cmd="cd $HOME/src && svn status -u ardour2 | grep \*",
		minutes_idle=5
)

clam.add_subtask( "List of new commits", [
	"cd $HOME/src/ardour2",
	{CMD:"svn log -r BASE:HEAD", INFO: lambda x:x },
	{CMD: "svn up", INFO: lambda x:x },
	] )

clam.add_deployment( [
	"cd $HOME/src/ardour2",
	{CMD: "svn up", INFO: lambda x:x },
	"rm -rf $HOME/src/tlocal/*",
	{INFO : lambda x: startTimer() }, 
	"scons PREFIX=$HOME/clamSandboxes/tlocal",
	{STATS : lambda x: {'build_time' : ellapsedTime() } },
	"scons install",
] )

Runner( clam, 
	continuous = True,
	remote_server_url = 'http://10.55.0.50/testfarm_server'
#	local_base_dir='/tmp'
)

