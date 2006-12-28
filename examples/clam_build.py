#! /usr/bin/python

import sys
sys.path.append('../src')
from task import *
from project import Project
from client import Client
from runner import Runner
import os, time

def countLines( path ):
	print "loc foro path:", path
	from commands import getoutput
	#print "find %s -name '*.?xx' -exec wc -l {} \;" % path.strip()
	lines =  getoutput("find %s -name '*.?xx' -exec wc -l {} \;" % path.strip() ).split("\n")
	#print lines
	return reduce( lambda x,y: x+y , map( lambda x: int(x.split()[0]), lines) )

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

def force_ok(output):
	return True

HOME = os.environ['HOME']
os.environ['LD_LIBRARY_PATH']='%s/clamSandboxes/tlocal/lib:/usr/local/lib' % HOME
os.environ['CLAM_TEST_DATA']='%s/clamSandboxes/CLAM-TestData' % HOME

def set_qtdir_to_qt4(x) :
	os.environ['QTDIR']='/usr/local/Trolltech/Qt-4.1.0/'
	os.environ['PKG_CONFIG_PATH']=os.environ['QTDIR']+'lib/pkgconfig'
def set_qtdir_to_qt3(x) :
	os.environ['QTDIR']='/usr/'

dapper = Client("linux_ubuntu_dapper")
dapper.brief_description = '<img src="http://clam.iua.upf.es/images/linux_icon.png"/> <img src="http://clam.iua.upf.es/images/ubuntu_icon.png"/>'
	

clam = Task(
	project = Project("CLAM"), 
	client = dapper, 
	task_name="with svn update" 
	)
clam.set_check_for_new_commits( 
		checking_cmd="cd $HOME/clamSandboxes && svn status -u testfarmTrunk | grep \*",
		minutes_idle=5
)

clam.add_subtask( "List of new commits", [
	"cd $HOME/clamSandboxes/testfarmTrunk",
	{CMD:"svn log -r BASE:HEAD", INFO: lambda x:x },
	{CMD: "svn up", INFO: lambda x:x },
	] )
clam.add_subtask("count lines of code", [
	{CMD:"echo $HOME/clamSandboxes/testfarmTrunk/CLAM", STATS: lambda x: {"clam_loc": countLines(x) } }
] )
clam.add_deployment( [
	{CMD: "echo setting QTDIR to qt3 path ", INFO: set_qtdir_to_qt3},
	"cd $HOME/clamSandboxes/testfarmTrunk/CLAM",
	"rm -rf $HOME/clamSandboxes/tlocal/*",
	"cd $HOME/clamSandboxes/testfarmTrunk/CLAM/scons/libs",
	"scons configure prefix=$HOME/clamSandboxes/tlocal with_osc_support=0",
	"scons",
	"scons install",
	"cd $HOME/clamSandboxes/tlocal/lib",
	{CMD:"for v in "" .0 .0.96; do for a in core processing vmqt vmfl audioio; do ln -s libclam_$a.so.0.96.1 libclam_$a.so$v; done; done", STATUS_OK: lambda x:True}
] )
clam.add_subtask("Unit Tests (with scons)", [
	{CMD: "echo setting QTDIR to qt3 path ", INFO: set_qtdir_to_qt3},
	"cd $HOME/clamSandboxes/testfarmTrunk/CLAM",
	"cd scons/tests",
	"scons test_data_path=$HOME/clamSandboxes/CLAM-TestData clam_sconstools=$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools install_prefix=$HOME/clamSandboxes/tlocal clam_prefix=$HOME/clamSandboxes/tlocal", # TODO: test_data_path and release
	"cd unit_tests",
	{INFO : start_timer}, 
	{CMD: "./UnitTests", INFO: lambda x:x},
	{STATS : exectime_unittests},
] )
clam.add_subtask("Functional Tests (with scons)", [
	{CMD: "echo setting QTDIR to qt3 path ", INFO: set_qtdir_to_qt3},
	"cd $HOME/clamSandboxes/testfarmTrunk/CLAM",
	"cd scons/tests",
	"scons test_data_path=$HOME/clamSandboxes/CLAM-TestData clam_sconstools=$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools install_prefix=$HOME/clamSandboxes/tlocal clam_prefix=$HOME/clamSandboxes/tlocal", # TODO: test_data_path and release
	"cd functional_tests",
	{INFO : start_timer}, 
	{CMD:"./FunctionalTests", INFO: lambda x:x},
	{STATS : exectime_functests},
] )
clam.add_subtask("CLAM Examples (with scons)", [
	{CMD: "echo setting QTDIR to qt3 path ", INFO: set_qtdir_to_qt3},
	"cd $HOME/clamSandboxes/testfarmTrunk/CLAM",
	"cd scons/examples",
	"scons clam_prefix=$HOME/clamSandboxes/tlocal",
] )
clam.add_subtask("SMSTools installation", [
	{CMD: "echo setting QTDIR to qt3 path ", INFO: set_qtdir_to_qt3},
	"cd $HOME/clamSandboxes/testfarmTrunk/SMSTools",
	"scons clam_sconstools=$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools install_prefix=$HOME/clamSandboxes/tlocal clam_prefix=$HOME/clamSandboxes/tlocal",
	"scons install",
	"$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools/changeExampleDataPath.py $HOME/clamSandboxes/tlocal/share/smstools ",
] )


clam.add_subtask('vmqt4 compilation and examples', [
	{CMD: "echo setting QTDIR to qt4 path ", INFO: set_qtdir_to_qt4},
	"cd $HOME/clamSandboxes/testfarmTrunk/Annotator/vmqt",
	'scons clam_sconstools=$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools install_prefix=$HOME/clamSandboxes/tlocal clam_prefix=$HOME/clamSandboxes/tlocal release=1 double=1',
	'scons examples',
] )
clam.add_subtask("Annotator installation", [
	{CMD: "echo setting QTDIR to qt4 path ", INFO: set_qtdir_to_qt4},
	"cd $HOME/clamSandboxes/testfarmTrunk/Annotator",
	"scons clam_vmqt4_path=vmqt clam_sconstools=$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools install_prefix=$HOME/clamSandboxes/tlocal clam_prefix=$HOME/clamSandboxes/tlocal",
	"scons install",
] )

clam.add_subtask("NetworkEditor installation", [
	{CMD: "echo setting QTDIR to qt3 path ", INFO: set_qtdir_to_qt3},
	"cd $HOME/clamSandboxes/testfarmTrunk/NetworkEditor",
	"scons install_prefix=$HOME/clamSandboxes/tlocal clam_prefix=$HOME/clamSandboxes/tlocal",
	"$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools/changeExampleDataPath.py $HOME/clamSandboxes/tlocal/share/smstools ",
] )

Runner( clam, 
	continuous = True,
	remote_server_url = 'http://10.55.0.50/testfarm_server'
#	local_base_dir='/tmp'
)

