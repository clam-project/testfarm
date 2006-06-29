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

import subprocess
from dirhelpers import *
from client import Client
from project import Project
from listeners import NullResultListener

class ServerListener(NullResultListener):
	"Receives and writes results as logs in a directory defined by project's name"
	def __init__(self, 
		client= Client('testing_client'), 
		logs_base_dir = '/tmp/testfarm_tests',
		project=None # TODO: project_name must not be None
	) :
		self.executions_needs_update = True
		self.client = client
		self.project = project
		self.logs_base_dir = logs_base_dir
		self.logfile = None
		self.idle_file = None
		
		assert project.name, "Error, project name was expected"

		create_dir_if_needed( "%s/%s" % (self.logs_base_dir, project.name) ) 
		self.logfile = log_filename( self.logs_base_dir, project.name, self.client.name )
		self.idle_file = idle_filename( self.logs_base_dir, project.name, self.client.name )
		self.client_info_file = client_info_filename(self.logs_base_dir, project.name, self.client.name )
		self.project_info_file = project_info_filename(self.logs_base_dir, project.name)
		self.__write_client_info(client)
		self.__write_project_info(project)
	
	def __append_log_entry(self, entry) :
		"Appends an entry to logfile"
		f = open(self.logfile, 'a+')
		f.write( entry )
		f.close()
		
	def __write_idle_info(self, idle_info) :
		f = open(self.idle_file, 'w')
		f.write( idle_info )
		f.close()
		
	def __write_client_info(self, client): # TODO what if a client needs to delete the descriptions from info file in another execution?
		if client.brief_description or client.long_description :
			f = open(self.client_info_file, 'w')
			if client.brief_description :
				entry = "('Brief description', '%s'),\n" % client.brief_description
				f.write( entry )
			if client.long_description :
				entry = "('Long description', '%s'),\n" % client.long_description	
				f.write( entry )
			attributes_sorted = client.attributes.keys()
			attributes_sorted.sort()
			for attribute_name in attributes_sorted:
				attribute_value = client.attributes[attribute_name] 
				entry = "('%s', '%s'),\n" % (attribute_name,attribute_value)
				f.write( entry )
			f.close()

	def __write_project_info(self, project):# TODO : remove CODE DUPLICATION 
		if project.brief_description or project.long_description :
			f = open(self.project_info_file, 'w')
			if project.brief_description :
				entry = "('Brief description', '%s'),\n" % project.brief_description
				f.write( entry )
			if project.long_description :
				entry = "('Long description', '%s'),\n" % project.long_description	
				f.write( entry )
			attributes_sorted = project.attributes.keys()
			attributes_sorted.sort()
			for attribute_name in attributes_sorted:
				attribute_value = project.attributes[attribute_name] 
				entry = "('%s', '%s'),\n" % (attribute_name,attribute_value)
				f.write( entry )
			f.close()
	
	def clean_log_files(self):
		"Deletes all log files"
		subprocess.call('rm -rf %s' % self.logs_base_dir, shell=True)

	def current_time(self):
		"Returns the current local time"
		return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

	def listen_end_command(self, command, ok, output, info, stats):
		entry = str( ('END_CMD', command, ok, output, info, stats) ) + ',\n'
		self.__append_log_entry(entry)

	def listen_begin_command(self, cmd):
		entry = "('BEGIN_CMD', '%s'),\n" % cmd 
		self.__append_log_entry(entry)
	
	#def listen_end_command(self, cmd):
	#	entry = "('END_CMD', '%s'),\n" % cmd
	#	self.__append_log_entry(entry)

	def listen_begin_subtask(self, taskname):
		entry = "('BEGIN_SUBTASK', '%s'),\n" % taskname 
		self.__append_log_entry(entry)

	def listen_end_subtask(self, taskname):
		entry = "('END_SUBTASK', '%s'),\n" % taskname
		self.__append_log_entry(entry)
	
	def listen_begin_task(self, task_name):
		entry = "\n('BEGIN_TASK', '%s', '%s'),\n" % (task_name, self.current_time())
		self.executions_needs_update = True
		self.__append_log_entry(entry)

	def listen_end_task(self, task_name, status):
		entry = "('END_TASK', '%s', '%s', '%s'),\n" % (task_name, self.current_time(), status)
		self.__append_log_entry(entry)
		self.executions_needs_update = True

	def executions_updated(self):
		self.executions_needs_update = False
	
	def listen_found_new_commits(self,  new_commits_found, next_run_in_seconds ):
		idle_dict = {}
		idle_dict['new_commits_found'] = new_commits_found
		idle_dict['date'] = self.current_time()
		idle_dict['next_run_in_seconds']=next_run_in_seconds	
		self.__write_idle_info( str( idle_dict ) )
			
	def listen_end_task_gently(self, task_name): #TODO: Refactor 
		"Ends task gently when a client aborts the execution, i.e, closes the logfile whith an 'END_TASK aborted' tuple"
		append_entry = "('END_TASK', '%s', '%s', 'Aborted'),\n" % (task_name, self.current_time())
		self.__append_log_entry(append_entry)	
