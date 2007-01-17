#! /usr/bin/python

import sys
sys.path.append('../src')
from os import environ
from task import *
from client import Client
from project import Project
from runner import Runner

# functions to parse minicppunit output
import re
def getNTests_line( line ) :
        executed = re.match(r".*Executed Tests:\ *(\d*)", line)
        passed   = re.match(r".*Passed Tests:\ *(\d*)", line)
        if executed: return (executed.group(1),0)
        if passed: return (0,passed.group(1))
        return (0,0)

def getNTests( out ) :
        dict = { 'passed_tests':0, '50':50, '100':100}
        for line in out.splitlines() :
                e,p = getNTests_line( line )
#               if e : dict['executed_tests'] = e
                if p : dict['passed_tests'] = p
        return dict
# end parser functions

environ['SVN_SSH']='ssh -i %s/.ssh/svn_id_dsa' % environ['HOME']

if sys.platform == "linux2":
	print "detected linux"
	machine = Client("testing-machine_linux_breezy")
	machine.brief_description ='<img src="http://clam.iua.upf.es/images/linux_icon.png"/> <img src="http://clam.iua.upf.es/images/ubuntu_icon.png"/>'
elif sys.platform == "darwin":
	print "detected mac osx"
	machine = Client("testing_machine_osx_tiger")
	machine.brief_description ='<img src="http://clam.iua.upf.es/images/apple_icon.png"/>'


essentia = Task(
		project = Project("essentia_trunk"),
		client = machine,
		task_name = "" 
		)

essentia.set_check_for_new_commits( 
	checking_cmd='cd $HOME/testfarm/essentia-sandboxes && svn status -u | grep \*', 
	minutes_idle=5
)


# change to false for checkout
do_update = True

if do_update:
	svn_command = 'svn update essentia-sandboxes/'
else:
	svn_command = 'svn checkout svn+ssh://testfarm@mtgdb.iua.upf.edu/essentia/trunk/ essentia-sandboxes/'

essentia.add_deployment([
	"cd $HOME/testfarm",
	"mkdir -p essentia-sandboxes",
	{CMD : "svn log -r BASE:HEAD essentia-sandboxes", INFO : lambda x:x },
	{CMD : svn_command, INFO : lambda x: x },
] )

essentia.add_subtask("build essentia", [
	"cd $HOME/testfarm/essentia-sandboxes/",
	"scons",
] )

essentia.add_subtask("build essentia python wrapper", [
	"cd $HOME/testfarm/essentia-sandboxes/",
	"scons python",
] )

essentia.add_subtask("install python bindings", [
	"cd $HOME/testfarm/essentia-sandboxes/",
	"sudo scons python install",
] )

essentia.add_subtask("build automatic cpp tests", [
	"cd $HOME/testfarm/essentia-sandboxes/test/",
	"scons",
] )

essentia.add_subtask("run automatic cpp tests", [
	"cd $HOME/testfarm/essentia-sandboxes/test/build/descriptortests",
	{CMD : "./test", INFO : lambda x: x, STATS : getNTests },
] )

essentia.add_subtask("run automatic python tests", [
	"cd $HOME/testfarm/essentia-sandboxes/test/src/pythontests",
	{CMD : "python tests.py", INFO : lambda x: x, STATS : getNTests },
] )

if sys.platform == "linux2":
	essentia.add_subtask("run valgrind with automatic tests (memory integrity checks)", [
		"cd $HOME/testfarm/essentia-sandboxes/test/build/descriptortests",
		{CMD : "valgrind --leak-check=full -q ./test | grep ^==[0-9]+===", INFO : lambda x:x, STATUS_OK: lambda x:True },
	] )

Runner ( 
	essentia,  
	# folder where to put dir log and html
	remote_server_url='http://10.55.0.50/testfarm_server',
	#local_base_dir ="/Users/aula324/testfarm/Mac-osX",
	continuous=True 
)
