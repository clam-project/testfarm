from mod_python import apache
from testfarmserver import TestFarmServer
import os, sys


def _log_filename(logs_base_dir, client_name) :
	return '%s/%s.testfarmlog' % (logs_base_dir, client_name)

def _idle_filename(logs_base_dir, client_name) :
	return '%s/%s.idle' % (logs_base_dir, client_name)

def _create_dir_if_needed(dir):
	if not os.path.isdir( dir ) :
		sys.stderr.write("Warning: directory '%s' is not available. Creating it." % dir)
		os.makedirs(dir)


_base_dir = '/tmp/remote_testfarm_logs'

server = TestFarmServer(
	logs_base_dir = _base_dir,
	html_dir = '/tmp/remote_testfarm_html/'
)

_create_dir_if_needed(_base_dir)


def append_log_entry(req, client_name, entry):
	filename = _log_filename(_base_dir, client_name)
	open( filename, 'a+').write(entry)
#	return "added: client=%s\nentry:%s\n" % (client_name, entry)
	server.update_static_html_files()
	return "log entry received ok"
	return apache.OK

def write_idle_info( req, client_name, idle_info ) :
	filename = _idle_filename(_base_dir, client_name)
	open( filename, 'w').write(idle_info)
	server.update_static_html_files()
	return "idle info received ok"
	return apache.OK
	

