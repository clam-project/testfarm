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

dapper = Client("linux_ubuntu_edgy_macbook")
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
clam.add_deployment( [
	{CMD: "echo setting QTDIR to qt3 path ", INFO: set_qtdir_to_qt3},
	"cd $HOME/clamSandboxes/testfarmTrunk/CLAM",
	{CMD: "svn up", INFO: lambda x:x },
	"rm -rf $HOME/clamSandboxes/tlocal/*",
	"cd $HOME/clamSandboxes/testfarmTrunk/CLAM/scons/libs",
	"scons configure prefix=$HOME/clamSandboxes/tlocal with_osc_support=0",
	"scons",
	"scons install",
	"cd $HOME/clamSandboxes/tlocal/lib",
	{CMD:"for a in core processing vmqt vmfl audioio; do ln -s libclam_$a.so.0.91.1 libclam_$a.so.0.91; ln -s libclam_$a.so.0.91.1 libclam_$a.so.0; ln -s libclam_$a.so.0.91.1 libclam_$a.so; done", STATUS_OK: lambda x:True}
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
	{CMD: "svn up", INFO: lambda x:x },
	"scons clam_sconstools=$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools install_prefix=$HOME/clamSandboxes/tlocal clam_prefix=$HOME/clamSandboxes/tlocal",
	"scons install",
	"$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools/changeExampleDataPath.py $HOME/clamSandboxes/tlocal/share/smstools ",
] )


clam.add_subtask('vmqt4 compilation and examples', [
	{CMD: "echo setting QTDIR to qt4 path ", INFO: set_qtdir_to_qt4},
	"cd $HOME/clamSandboxes/testfarmTrunk/Annotator/vmqt",
	{CMD: "svn up", INFO: lambda x:x },
	'scons clam_sconstools=$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools install_prefix=$HOME/clamSandboxes/tlocal clam_prefix=$HOME/clamSandboxes/tlocal release=1 double=1',
	'scons examples',
] )
clam.add_subtask("Annotator installation", [
	{CMD: "echo setting QTDIR to qt4 path ", INFO: set_qtdir_to_qt4},
	"cd $HOME/clamSandboxes/testfarmTrunk/Annotator",
	{CMD: "svn up", INFO: lambda x:x },
	"scons clam_vmqt4_path=vmqt clam_sconstools=$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools install_prefix=$HOME/clamSandboxes/tlocal clam_prefix=$HOME/clamSandboxes/tlocal",
	"scons install",
] )

clam.add_subtask("NetworkEditor installation", [
	{CMD: "echo setting QTDIR to qt3 path ", INFO: set_qtdir_to_qt3},
	"cd $HOME/clamSandboxes/testfarmTrunk/NetworkEditor",
	{CMD: "svn up", INFO: lambda x:x },
	"scons install_prefix=$HOME/clamSandboxes/tlocal clam_prefix=$HOME/clamSandboxes/tlocal annotator_path=$HOME/clamSandboxes/testfarmTrunk/Annotator",
	"$HOME/clamSandboxes/testfarmTrunk/CLAM/scons/sconstools/changeExampleDataPath.py $HOME/clamSandboxes/tlocal/share/smstools ",
] )

'''
clam.add_subtask("Deploy OLD (srcdeps) build system", [
	"cd $HOME/clamSandboxes/testing-clam/build/srcdeps",
	"make",
	"cd ..",
	"pwd && autoconf",
	"./configure"
	
])
clam.add_subtask("Unit Tests (with srcdeps)", [
	{CMD: "echo setting QTDIR to qt3 path ", INFO: set_qtdir_to_qt3},
	"cd $HOME/clamSandboxes/testfarmTrunk/CLAM",
	"cd build/Tests/UnitTests",
	"make depend",
	"CONFIG=release make",
	{INFO : start_timer}, 
#	{CMD:"./UnitTests", INFO: lambda x : x},
	{CMD:"./UnitTests"},
	{STATS : exectime_unittests}

] )
clam.add_subtask("Functional Tests (with srcdeps)", [
	{CMD: "echo setting QTDIR to qt3 path ", INFO: set_qtdir_to_qt3},
	"cd $HOME/clamSandboxes/testfarmTrunk/CLAM",
	"cd build/Tests/FunctionalTests",
	"make depend",
	"CONFIG=release make",
	{INFO : start_timer}, 
#	{CMD:"./FunctionalTests", INFO: lambda x : x},
	{CMD:"./FunctionalTests"},
	{STATS : exectime_functests}
] )

'''
clam.add_subtask("Deploy SMSTools srcdeps branch for SMSBase tests", [
	"cd $HOME/clamSandboxes",
	"rm -rf testing-smstools-srcdeps",
	"cvs co -r srcdeps-build-system-branch -d testing-smstools-srcdeps CLAM_SMSTools",
	'echo "CLAM_PATH=$HOME/clamSandboxes/testfarmTrunk/CLAM/" > testing-smstools-srcdeps/build/clam-location.cfg'
] )

clam.add_subtask("Testing SMSTransformations (using SMSTools srcdeps branch)", [
	"cd $HOME/clamSandboxes",
	"cd testing-smstools-srcdeps/build/FunctionalTests",
	"make depend",
	"CONFIG=debug make", #release doesn't work
	{CMD: "./SMSToolsTests", INFO: lambda x : x}
] )
'''


Runner( clam, 
#	continuous = True,
#	remote_server_url = 'http://10.55.0.50/testfarm_server'
	local_base_dir='/tmp'
)

