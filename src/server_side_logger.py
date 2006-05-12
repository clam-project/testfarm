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
from client import Client
from project import Project
from dirhelpers import *
import os, sys


_logs_base_dir = '/var/www/testfarm_logs'
_html_base_dir = '/var/www/testfarm_html'

server = Server(
	logs_base_dir = _logs_base_dir,
	html_base_dir = _html_base_dir
)

create_dir_if_needed(_logs_base_dir)
create_dir_if_needed(_html_base_dir)

def create_dirs(req, project_name):
	create_dir_if_needed('%s/%s/' % (_logs_base_dir, project_name) ) #TODO is there a better way?
	create_dir_if_needed('%s/%s/' % (_html_base_dir, project_name) )
	return "remote dirs Ok"

def append_log_entry(req, project_name, client_name, entry):
	server.project_name = project_name
	filename = log_filename(_logs_base_dir, project_name, client_name)
	f = open( filename, 'a+')
	f.write(entry)
	f.close()
	server.update_static_html_files()
	return "remote OK"
	return apache.OK

def write_idle_info( req, project_name, client_name, idle_info ) :
	server.project_name = project_name
	filename = idle_filename(_logs_base_dir, project_name, client_name)
	f = open( filename, 'w')
	f.write(idle_info)
	f.close()
	server.update_static_html_files()
	return "remote Ok"
	return apache.OK

def write_client_info(req, client_name, project_name, client_info): 
	filename = client_info_filename(_logs_base_dir, project_name, client_name)
	f = open(filename, 'w')
	f.write( client_info )
	return "remote client Ok"


def write_project_info(req, project_name, project_info):# TODO : remove CODE DUPLICATION 
	filename = project_info_filename(_logs_base_dir, project_name)
	f = open(filename, 'w')
	f.write( project_info )
	f.close()
	return "remote project Ok"



	

