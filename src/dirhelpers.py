 #! /usr/bin/python

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

import os

def remove_path_and_extension( path ):
	return os.path.splitext( os.path.basename( path ) )[0]


def log_filename(logs_base_dir, project_name, client_name) :
	return '%s/%s/%s.testfarmlog' % (logs_base_dir, project_name, client_name)

def idle_filename(logs_base_dir, project_name, client_name) :
	return '%s/%s/%s.idle' % (logs_base_dir, project_name, client_name)

def client_info_filename(logs_base_dir, project_name, client_name) :
	return '%s/%s/%s.info' % (logs_base_dir, project_name, client_name)

def project_info_filename(logs_base_dir, project_name) :
	return '%s/%s/%s.info' % (logs_base_dir, project_name, project_name)

def create_dir_if_needed(dir):
	if not os.path.isdir( dir ) :
#		sys.stderr.write("\nWarning: directory '%s' is not available. Creating it." % dir)
		os.makedirs(dir)
