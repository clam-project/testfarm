#! /usr/bin/python

import sys
sys.path.append('../src')
from os import environ

from task import *
from client import Client
from project import Project
from runner import Runner

def pass_text(text) :
	return text


environ['SVN_SSH']='ssh -i %s/.ssh/svn_id_dsa' % environ['HOME']

cd_essentia = "cd $HOME/essentia-sandboxes/clean-essentia/trunk"

essentia_update = 'svn update clean-essentia/trunk/'
essentia_checkout = 'svn checkout svn+ssh://testfarm@mtgdb.iua.upf.edu/essentia/trunk/ clean-essentia/trunk/'

if sys.platform == "linux2":
	lib_path = "LD_LIBRARY_PATH"
	machine = "testing-machine_linux_breezy"
elif sys.platform == "darwin":
	lib_path = "DYLD_LIBRARY_PATH"
	machine = "testing_machine_osx_tiger"


essentia = Task(
		project = Project("essentia_trunk"),
		client = Client(machine),
		task_name = "" 
		)

essentia.add_subtask("TODO fix bug: update html at begin time ", [] )

essentia.add_checking_for_new_commits( 
	checking_cmd='cd $HOME/essentia-sandboxes && svn status -u clean-essentia/trunk | grep \*', 
	minutes_idle=5
)

essentia.add_deployment([
	"cd $HOME/",
	"mkdir -p essentia-sandboxes",
	"cd essentia-sandboxes",
	#"rm -fr /tmp/essentia/",
	#"rm -fr clean-essentia/trunk/build",
	#"rm -fr clean-essentia/trunk/algorithms",
	#"rm -fr clean-essentia/trunk/test/build",
	#{CMD : "svn diff --revision HEAD clean-essentia/trunk", INFO: pass_text},
	{CMD : essentia_update, INFO : pass_text },
] )

essentia.add_subtask("build core libs", [
	cd_essentia,
	"scons base prefix=/tmp/essentia/",
	"scons install base prefix=/tmp/essentia",
] )

essentia.add_subtask("build plugin libs", [
	cd_essentia,
	"scons prefix=/tmp/essentia",
	"scons install prefix=/tmp/essentia",
] )

essentia.add_subtask("automatic tests", [
	cd_essentia,
	"cd test",
	"scons prefix=/tmp/essentia",
	"cd build/unittests/descriptortests/",
	{CMD : "%s=/tmp/essentia/lib/ ./test" % lib_path, INFO : pass_text},
] )


Runner ( 
	essentia,  
	remote_server_url='http://10.55.0.66/testfarm_server',
	continuous=True 
)
