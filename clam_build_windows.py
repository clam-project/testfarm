#! /usr/bin/python

from os import environ
from testfarmclient import *

def pass_text(text) :
	return text

def force_ok(text):
	return True

def minicppunit_parser(text):
	result = []
	in_summary = False
	for line in text.split('\n'):
		if not in_summary and 'Summary:' in line:
			in_summary = True
			result.append( line )
		if in_summary :
			result.append( line )
		return "\n".join(result)

clam_checkout = ''
cd_clam = 'cd f:\\clam-sandboxes'

clam = Repository("CLAM")

'''clam.add_checking_for_new_commits( 
	checking_cmd='cd g:\\sandbox\\clam-sandbox\\ && "c:\\program files\\svn\\svn" status -u clean-clam/trunk | grep \*', 
	minutes_idle=5
)'''

clam.add_deployment_task([
    cd_clam,
    'cd CLAM-0.90.0\\scons\\libs',
    'vcvars32.bat', 
    'scons configure',
    'scons',
    'scons install'
        
#	{CMD : clam_checkout, INFO : pass_text },
] )


TestFarmClient( 
	'testing-machine_windows', 
	clam,  
	#generated_html_path='./html',
	#logs_path='g:\\sandbox\\clam-sandbox\\testfarm_logs',
	remote_server_url="http://10.55.0.66/testfarm_server",
	continuous=False 
)
