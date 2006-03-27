from mod_python import apache
from testfarmserver import TestFarmServer
import os, sys


def _log_filename(logs_base_dir, repository_name, client_name) :
	return '%s/%s/%s.testfarmlog' % (logs_base_dir, repository_name, client_name)

def _idle_filename(logs_base_dir, repository_name, client_name) :
	return '%s/%s/%s.idle' % (logs_base_dir, repository_name, client_name)

def _create_dir_if_needed(dir):
	print "=================== CREATING DIR if needed", dir
	if not os.path.isdir( dir ) :
		sys.stderr.write("Warning: directory '%s' is not available. Creating it." % dir)
		os.makedirs(dir)


_logs_base_dir = '/tmp/remote_testfarm_logs'
_html_base_dir = '/tmp/remote_testfarm_html'

server = TestFarmServer(
	logs_base_dir = _logs_base_dir,
	html_base_dir = _html_base_dir
)

_create_dir_if_needed(_logs_base_dir)
_create_dir_if_needed(_html_base_dir)

def append_log_entry(req, repository_name, client_name, entry):
	server.repository_name = repository_name
	filename = _log_filename(_logs_base_dir, repository_name, client_name)
	f = open( filename, 'a+')
	f.write(entry)
	f.close()
	server.update_static_html_files()
	return "log entry received"
	return apache.OK

def write_idle_info( req, repository_name, client_name, idle_info ) :
	server.repository_name = repository_name
	_create_dir_if_needed('%s/%s/' % (_logs_base_dir, repository_name) ) #TODO is there a better way?
	_create_dir_if_needed('%s/%s/' % (_html_base_dir, repository_name) )
	filename = _idle_filename(_logs_base_dir, repository_name, client_name)
	f = open( filename, 'w')
	f.write(idle_info)
	f.close()
	server.update_static_html_files()
	return "idle info received"
	return apache.OK
	

