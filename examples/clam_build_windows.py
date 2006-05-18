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

def force_ok(text):
	return True
def filter_cvs_update( text ):
	dont_start_interr = lambda line : not line or not line[0]=='?'
	result = filter(dont_start_interr, text.split('\n') )	
	return '\n'.join(result)

def set_qtdir_to_qt4(x) : environ['QTDIR']='f:\\Qt4.1.1\\'
def set_qtdir_to_qt3(x) : environ['QTDIR']='f:\\clam-external-libs\\qt3\\'

cd_clam = 'cd f:\\clam-sandboxes'

clam = Task(
	project = Project("CLAM"), 
	client = Client("testing_machine-windows"), 
	task_name="with cvs update" 
	)


clam.add_checking_for_new_commits( 
	checking_cmd='cd f:\\clam-sandboxes\\ && cvs -nq up -dP testing-clam testing-vmqt testing-annotator testing-neteditor testing-smstools | grep ^[UP]',  
	minutes_idle=5
)

clam.add_deployment([
	cd_clam,
	"cd testing-clam",
	{ CMD: "cvs -q up -dP", INFO: filter_cvs_update },
	cd_clam,
	'cd testing-clam\\scons\\libs',
	{INFO: set_qtdir_to_qt3},
'scons configure prefix=f:\\clam-sandboxes\\local sandbox_path=f:\\clam-external-libs  qt_includes=f:\\clam-external-libs\\qt\\include qt_libs=f:\\clam-external-libs\\qt\\lib release=1 double=1',
	'scons',
	'scons install',
#	'scons install', #TODO bug? check if repeating scons install is really necessary.
] )

clam.add_subtask('unit tests', [
	cd_clam,
	'cd testing-clam\\scons\\tests',
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=f:\\clam-sandboxes\\local cppunit_prefix=f:\\clam-external-libs\cppunit test_data_path=f:\\clam-sandboxes\\CLAM-TestData release=1 double=1 unit_tests',
	'cd unit_tests',
	{CMD: 'UnitTests.exe', INFO: lambda x:x, STATUS_OK: force_ok },
	])

clam.add_subtask('functional test', [
	cd_clam,
	'cd testing-clam\\scons\\tests',
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=f:\\clam-sandboxes\\local cppunit_prefix=f:\\clam-external-libs\cppunit test_data_path=f:\\clam-sandboxes\\CLAM-TestData release=1 double=1 functional_tests',
	'cd functional_tests',
	{CMD: 'FunctionalTests.exe', INFO: lambda x:x, STATUS_OK: force_ok },
	])

clam.add_subtask('clam examples compilation', [
	cd_clam,
	'cd testing-clam\\scons\\examples',
	'scons clam_prefix=f:\\clam-sandboxes\\local release=1 double=1',
	])


clam.add_subtask('smstools compilation', [
	cd_clam,
	'cd testing-smstools',
	{ CMD: "cvs -q up -dP", INFO: filter_cvs_update },
	'cd scons\\QtSMSTools',
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=\\clam-sandboxes\\local release=1 double=1'
] )
clam.add_subtask('network editor compilation', [
	cd_clam,
	'cd testing-neteditor',
	{ CMD: "cvs -q up -dP", INFO: filter_cvs_update },
	'cd scons\\',
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=\\clam-sandboxes\\local release=1 double=1'
] )

clam.add_subtask('vmqt compilation and examples', [
	cd_clam,
	'cd testing-vmqt',
	{ CMD: "cvs -q up -dP", INFO: filter_cvs_update },
	{ INFO: set_qtdir_to_qt4 },
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=\\clam-sandboxes\\local clam_sconstools=f:\\clam-sandboxes\\testing-clam\\scons\\sconstools release=1 double=1'
	'scons examples',
] )


clam.add_subtask('annotator compilation', [
	cd_clam,
	'cd testing-annotator',
	{ CMD: "cvs -q up -dP", INFO: filter_cvs_update },
	'cd src',
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=\\clam-sandboxes\\local clam_sconstools=f:\\clam-sandboxes\\testing-clam clam_vmqt4_path=f:\\clam-sandboxes\\testing-vmqt release=1 double=1'
] )



Runner( 
	clam,  
	remote_server_url="http://10.55.0.66/testfarm_server",
)
