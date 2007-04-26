#! /usr/bin/python
#
# IMPORTANT: maintained (so up-to-date) clam-testfarm scripts can be
# found in the clam repo, in CLAM/scripts. Checkout command:
# svn co http://iua-share.upf.edu/svn/clam/trunk clam
# So it's possible this script won't work.
#

# vcvars32.bat must be run in windows before this script

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

def force_ok(text):
	return True

def filter_cvs_update( text ):
	dont_start_interr = lambda line : not line or not line[0]=='?'
	result = filter(dont_start_interr, text.split('\n') )	
	return '\n'.join(result)

def filter_svn_update( text ):
	return text

#update_command = { CMD: "cvs -q up -Pd", INFO: filter_cvs_update }
update_command = { CMD: "svn up", INFO: filter_svn_update }

def set_qtdir_to_qt4_fn(x) : 
	os.environ['QTDIR']='f:\\Qt4.1.1\\'
	return 'QTDIR set to ' + os.environ['QTDIR']
set_qtdir_to_qt4 = {CMD: "echo seting QTDIR to qt4 path ", INFO: set_qtdir_to_qt4_fn}

def set_qtdir_to_qt3_fn(x) : 
	os.environ['QTDIR']='f:\\clam-external-libs\\qt\\'
	return 'QTDIR set to ' + os.environ['QTDIR']
set_qtdir_to_qt3 = {CMD: "echo seting QTDIR to qt3 path ", INFO: set_qtdir_to_qt3_fn}

os.environ['EXTERNALDLLDIR']='f:\\clam-external-libs\dlls'
os.environ['CLAM_TEST_DATA']='f:\\clam-sandboxes\\CLAM-TestData'

cd_clam = 'cd f:\\clam-sandboxes'
install_path = 'f:\\clam-sandboxes\\tlocal'
sconstools_path = 'f:\\clam-sandboxes\\trunk-testfarm\\CLAM\\scons\\sconstools'

windows = Client("windows_xp")
windows.brief_description = '<img src="http://clam.iua.upf.es/images/windows_icon.png"/>'

clam = Task(
	project = Project("CLAM"), 
	client = windows, 
	task_name="with cvs update" 
	)

clam.set_check_for_new_commits(
	checking_cmd = "cd f:\\clam-sandboxes\\trunk-testfarm\\ && svn status -u | grep \\*",
	minutes_idle=5
)

clam.add_deployment([
	cd_clam,
	"cd trunk-testfarm\\CLAM",
	update_command,
	cd_clam,
	"rm -rf tlocal\\*",
	'cd trunk-testfarm\\CLAM\\scons\\libs',
	set_qtdir_to_qt3,
	'scons configure'+
	' prefix=%s'%install_path +
	' sandbox_path=f:\\clam-external-libs' +
	' qt_includes=f:\\clam-external-libs\\qt\\include' +
	' qt_libs=f:\\clam-external-libs\\qt\\lib' +
	' with_portmidi=1 release=1 double=1',
	'scons',
	'scons install',
#	'scons install', #TODO bug? check if repeating scons install is really necessary.
] )

clam.add_subtask('unit tests', [
	cd_clam,
	'cd trunk-testfarm\\CLAM\\scons\\tests',
	set_qtdir_to_qt3,
	'scons unit_tests'+
	' clam_prefix=%s'%install_path +
	' install_prefix=%s'%install_path +
	' cppunit_prefix=f:\\clam-external-libs\\cppunit' +
	' test_data_path=f:\\clam-sandboxes\\CLAM-TestData' +
	' release=1 double=1',
	'cd unit_tests',
	{CMD: 'UnitTests.exe', INFO: lambda x:x, STATUS_OK: force_ok },
	])

clam.add_subtask('functional test', [
	cd_clam,
	'cd trunk-testfarm\\CLAM\\scons\\tests',
	set_qtdir_to_qt3,
	'scons functional_tests' +
	' clam_prefix=%s'%install_path +
	' install_prefix=%s'%install_path +
	' cppunit_prefix=f:\\clam-external-libs\\cppunit' +
	' test_data_path=f:\\clam-sandboxes\\CLAM-TestData' +
	' release=1 double=1',
	'cd functional_tests',
	{CMD: 'FunctionalTests.exe', INFO: lambda x:x, STATUS_OK: force_ok },
	])

clam.add_subtask('clam examples compilation', [
	cd_clam,
	'cd trunk-testfarm\\CLAM\\scons\\examples',
	set_qtdir_to_qt3,
	'scons' +
	' clam_prefix=%s'%install_path +
	' release=1 double=1',
	])


clam.add_subtask('smstools compilation', [
	cd_clam,
	'cd trunk-testfarm\\SMSTools',
	update_command,
	set_qtdir_to_qt3,
	'scons' +
	' clam_prefix=%s'%install_path +
	' install_prefix=%s'%install_path +
	' clam_sconstools=%s'%sconstools_path +
	' release=1 double=1'
] )
clam.add_subtask('smstools install', [
	cd_clam,
	'cd trunk-testfarm\\SMSTools',
	'scons install'
] )
clam.add_subtask('smstools package', [
	cd_clam,
	'cd trunk-testfarm\\SMSTools',
	'scons package'
])


clam.add_subtask('vmqt compilation and examples', [
	cd_clam,
	'cd trunk-testfarm\\Annotator\\vmqt',
	update_command,
	set_qtdir_to_qt4,
	'scons ' +
	' clam_prefix=%s'%install_path +
	' install_prefix=%s'%install_path +
	' clam_sconstools=%s'%sconstools_path +
	' release=1 double=1',
	'scons examples'
] )


clam.add_subtask('annotator compilation', [
	cd_clam,
	'cd trunk-testfarm\\Annotator',
	update_command,
	set_qtdir_to_qt4,
	'scons' +
	' clam_prefix=%s'%install_path +
	' install_prefix=%s'%install_path +
	' clam_sconstools=%s'%sconstools_path +
	' release=1 double=1'
] )

clam.add_subtask('annotator install', [
	cd_clam,
	'cd trunk-testfarm\\Annotator',
	'scons install'
] )
clam.add_subtask('annotator package', [
	cd_clam,
	'cd trunk-testfarm\\Annotator\\SimacServicesClient',
	'buildExeFromPython.py',
	'cd ..',
	'scons package'
] )

clam.add_subtask('network editor compilation', [
	cd_clam,
	'cd trunk-testfarm\\NetworkEditor',
	update_command,
	set_qtdir_to_qt4,
	'scons' +
	' clam_prefix=%s'%install_path +
	' install_prefix=%s'%install_path +
	' clam_sconstools=%s'%sconstools_path +
	' annotator_path=..\\Annotator' +
	' cppunit_prefix=f:\\clam-external-libs\\cppunit' +
	' release=1 double=1'
] )
clam.add_subtask('neteditor install', [
	cd_clam,
	'cd trunk-testfarm\\NetworkEditor',
	'scons install'
])
clam.add_subtask('neteditor package', [
	cd_clam,
	'cd trunk-testfarm\\NetworkEditor',
	'scons package'
])

clam.add_subtask('VstPrototyper', [
	cd_clam,
	'cd trunk-testfarm\\NetworkEditor\\src\\\\vstprototyper',
	'scons' +
	' install_prefix=%s'%install_path +
	' clam_prefix=%s'%install_path +
	' clam_sconstools=%s'%sconstools_path +
	' vstsdk_path=f:\\clam-external-libs\\\\vstsdk2.3'
] )



Runner( 
	clam,  
	remote_server_url="http://10.55.0.50/testfarm_server",
	local_base_dir="f:\\tmp\\",
	continuous = True,
	verbose = True,
)
