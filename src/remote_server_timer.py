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

from server import Server
import os, time

_logs_base_dir = '/var/www/testfarm_logs'
_html_base_dir = '/var/www/testfarm_html'

_list_dir = []

server = Server(
	logs_base_dir = _logs_base_dir,
	html_base_dir = _html_base_dir
)

def update_projects_static_html_files():
	"Updates all projects's html files"
	list_dir = os.listdir(_html_base_dir)
	print list_dir
	for entry in list_dir:
		entry_path = os.path.join(_html_base_dir, entry)
		if os.path.isdir(entry_path):
			server.project_name = entry
			server.write_missing_details_static_html()
			server.update_static_html_files()
			

while True:
	update_projects_static_html_files()
	time.sleep( 30 )

