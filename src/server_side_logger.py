#
#  Copyright (c) 2006 Pau Arumi, Bram de Jong, Mohamed Sordo 
#  and Universitat Pompeu Fabra
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
 
from mod_python import apache
from server import Server
import os, sys


def _log_filename(logs_base_dir, project_name, client_name) :
	return '%s/%s/%s.testfarmlog' % (logs_base_dir, project_name, client_name)

def _idle_filename(logs_base_dir, project_name, client_name) :
	return '%s/%s/%s.idle' % (logs_base_dir, project_name, client_name)

def _create_dir_if_needed(dir):
	if not os.path.isdir( dir ) :
		sys.stderr.write("Warning: directory '%s' is not available. Creating it." % dir)
		os.makedirs(dir)


_logs_base_dir = '/var/www/testfarm_logs'
_html_base_dir = '/var/www/testfarm_html'

server = TestFarmServer(
	logs_base_dir = _logs_base_dir,
	html_base_dir = _html_base_dir
)

_create_dir_if_needed(_logs_base_dir)
_create_dir_if_needed(_html_base_dir)

def append_log_entry(req, project_name, client_name, entry):
	server.project_name = project_name
	filename = _log_filename(_logs_base_dir, project_name, client_name)
	f = open( filename, 'a+')
	f.write(entry)
	f.close()
	server.update_static_html_files()
	return "remote OK"
	return apache.OK

def write_idle_info( req, project_name, client_name, idle_info ) :
	server.project_name = project_name
	_create_dir_if_needed('%s/%s/' % (_logs_base_dir, project_name) ) #TODO is there a better way?
	_create_dir_if_needed('%s/%s/' % (_html_base_dir, project_name) )
	filename = _idle_filename(_logs_base_dir, project_name, client_name)
	f = open( filename, 'w')
	f.write(idle_info)
	f.close()
	server.update_static_html_files()
	return "remote Ok"
	return apache.OK
	

