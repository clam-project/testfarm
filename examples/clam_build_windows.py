#! /usr/bin/python

import sys
sys.path.append('../src')
from os import environ
from testfarmclient import *

def pass_text(text) :
	return text

def force_ok(text):
	return True


def filter_cvs_update( text ):
	dont_start_interr = lambda line : not line or not line[0]=='?'
	result = filter(dont_start_interr, text.split('\n') )	
	return '\n'.join(result)

def set_qtdir_to_qt4(x) : environ['QTDIR']='f:\\Qt4.1.1\\'
def set_qtdir_to_qt3(x) : environ['QTDIR']='f:\\clam-external-libs\\qt3\\'

cd_clam = 'cd f:\\clam-sandboxes'

clam = Repository("CLAM")

clam.add_checking_for_new_commits( 
	checking_cmd='cd f:\\clam-sandboxes\\ && cvs -nq up -dP testing-clam testing-vmqt testing-annotator testing-neteditor testing-smstools | grep ^[UP]',  
	minutes_idle=5
)

clam.add_deployment_task([
	cd_clam,
	"cd testing-clam",
	{ CMD: "cvs -q up -dP", INFO: filter_cvs_update },
	cd_clam,
	'cd testing-clam\\scons\\libs',
	{INFO: set_qtdir_to_qt3},
'scons configure prefix=f:\\clam-sandboxes\\local sandbox_path=f:\\clam-external-libs  qt_includes=f:\\clam-external-libs\\qt\\include qt_libs=f:\\clam-external-libs\\qt\\lib release=1 double=1',
	'scons',
	'scons install',
	'scons install', #TODO bug? check if repeating scons install is really necessary.
] )

clam.add_task('unit tests', [
	cd_clam,
	'cd testing-clam\\scons\\tests',
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=f:\\clam-sandboxes\\local cppunit_prefix=f:\\clam-external-libs\cppunit test_data_path=f:\\clam-sandboxes\\CLAM-TestData release=1 double=1 unit_tests',
	'cd unit_tests',
	{CMD: 'UnitTests.exe', INFO: pass_text, STATUS_OK: force_ok },
	])

clam.add_task('functional test', [
	cd_clam,
	'cd testing-clam\\scons\\tests',
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=f:\\clam-sandboxes\\local cppunit_prefix=f:\\clam-external-libs\cppunit test_data_path=f:\\clam-sandboxes\\CLAM-TestData release=1 double=1 functional_tests',
	'cd functional_tests',
	{CMD: 'FunctionalTests.exe', INFO: pass_text, STATUS_OK: force_ok },
	])

clam.add_task('clam examples compilation', [
	cd_clam,
	'cd testing-clam\\scons\\examples',
	'scons clam_prefix=f:\\clam-sandboxes\\local release=1 double=1',
	])


clam.add_task('smstools compilation', [
	cd_clam,
	'cd testing-smstools',
	{ CMD: "cvs -q up -dP", INFO: filter_cvs_update },
	'cd scons\\QtSMSTools',
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=\\clam-sandboxes\\local release=1 double=1'
] )
clam.add_task('network editor compilation', [
	cd_clam,
	'cd testing-neteditor',
	{ CMD: "cvs -q up -dP", INFO: filter_cvs_update },
	'cd scons\\',
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=\\clam-sandboxes\\local release=1 double=1'
] )

clam.add_task('vmqt compilation and examples', [
	cd_clam,
	'cd testing-vmqt',
	{ CMD: "cvs -q up -dP", INFO: filter_cvs_update },
	{ INFO: set_qtdir_to_qt4 },
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=\\clam-sandboxes\\local clam_sconstools=f:\\clam-sandboxes\\testing-clam\\scons\\sconstools release=1 double=1'
	'scons examples',
] )


clam.add_task('annotator compilation', [
	cd_clam,
	'cd testing-annotator',
	{ CMD: "cvs -q up -dP", INFO: filter_cvs_update },
	'cd src',
	'scons clam_prefix=f:\\clam-sandboxes\\local install_prefix=\\clam-sandboxes\\local clam_sconstools=f:\\clam-sandboxes\\testing-clam clam_vmqt4_path=f:\\clam-sandboxes\\testing-vmqt release=1 double=1'
] )



TestFarmClient( 
	'testing-machine_windows', 
	clam,  
	#generated_html_path='./html',
	#logs_path='g:\\sandbox\\clam-sandbox\\testfarm_logs',
	remote_server_url="http://10.55.0.66/testfarm_server",
	continuous=True
)
