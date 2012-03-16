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

import datetime
from service_proxy import ServiceProxy
from listeners import NullResultListener
from task import get_command_and_parsers
#
# Server Listener Proxy
#

class ServerListenerProxy(NullResultListener):
	"Receives and sends results to a remote server logger"
	def __init__(self, client, service_url, project) : # TODO: control project and client if None
		self.client = client
		self.webservice = ServiceProxy(service_url)
		self.project = project
		self._create_dirs()
		self._write_project_info(self.project)
		self._write_client_info(self.client)

	def _remote_call(self, method, **kwds) :
		result = self.webservice.remote_call(method, **kwds)
		if str(result) == '0' : return
		print "Remote error:", result
	
	def _create_dirs(self):
		self._remote_call(
			"create_dirs", 
			project_name=self.project.name,
			) 
			
	def _append_log_entry(self, entry) :
		"Appends an entry to logfile"
		self._remote_call(
			"append_log_entry", 
			project_name=self.project.name, 
			client_name=self.client.name, 
			entry=entry,
			)

	def _write_idle_info(self, idle_info ):
		self._remote_call(
			"write_idle_info",
			project_name=self.project.name, 
			client_name=self.client.name, 
			idle_info=idle_info,
			)
			
	def _write_client_info(self, client):
		if client.brief_description or client.long_description :
			entries = ""
			if client.brief_description :
				entries += "('Brief description', '%s'),\n" % client.brief_description
			if client.long_description :
				entries += "('Long description', '%s'),\n" % client.long_description	
			attributes_sorted = client.attributes.keys()
			attributes_sorted.sort()
			for attribute_name in attributes_sorted:
				attribute_value = client.attributes[attribute_name] 
				entries += "('%s', '%s'),\n" % (attribute_name,attribute_value)
			
			self._remote_call(
				"write_client_info",
				project_name=self.project.name,
				client_name=self.client.name,
				client_info = entries,
				) 

	def _write_project_info(self, project):# TODO : remove CODE DUPLICATION 
		if project.brief_description or project.long_description :
			entries = ""
			if project.brief_description :
				entries += "('Brief description', '%s'),\n" % project.brief_description
			if project.long_description :
				entries += "('Long description', '%s'),\n" % project.long_description	
			attributes_sorted = project.attributes.keys()
			attributes_sorted.sort()
			for attribute_name in attributes_sorted:
				attribute_value = project.attributes[attribute_name] 
				entries += "('%s', '%s'),\n" % (attribute_name,attribute_value)

			self._remote_call(
				"write_project_info",
				project_name=self.project.name,
				project_info=entries,
				) 

	def __write_task_info(self, task):	
		entries = "('BEGIN_TASK', '%s'),\n" % task.name
		for subtask in task.subtasks :
			entries += "('BEGIN_SUBTASK', '%s'),\n" % subtask.name 
			for maybe_dict in subtask.commands :
				cmd, _, _, _ = get_command_and_parsers(maybe_dict)
				entries += "('CMD', '%s'),\n" % cmd
			entries += "('END_SUBTASK', '%s'),\n" % subtask.name 
		entries += "('END_TASK', '%s'),\n" % task.name
		self._remote_call(
			"write_task_info",
			project_name = task.project.name,
			client_name = task.client.name,
			task_name = task.name,
			task_info = entries,
			)
 
	def current_time(self):
		"Returns the current local time"
		return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

	def listen_end_command(self, command, ok, output, info, stats):
		entry = str( ('END_CMD', command, ok, output, info, stats) ) + ',\n'
		self._append_log_entry('\t\t' + entry)

	def listen_begin_command(self, cmd):
		entry = "('BEGIN_CMD', '%s'),\n" % cmd 
		self._append_log_entry('\t\t' + entry)

	def listen_begin_subtask(self, subtaskname):
		entry = "('BEGIN_SUBTASK', '%s'),\n" % subtaskname 
		self._append_log_entry('\t' + entry)

	def listen_end_subtask(self, subtaskname):
		entry = "('END_SUBTASK', '%s'),\n" % subtaskname
		self._append_log_entry('\t' + entry)
	
	def listen_begin_task(self, task_name):
		entry = "('BEGIN_TASK', '%s', '%s'),\n" % (task_name, self.current_time())
		self._append_log_entry('\n' + entry)

	def listen_end_task(self, task_name, status):
		entry = "('END_TASK', '%s', '%s', '%s'),\n" % (task_name, self.current_time(), status)
		self._append_log_entry(entry)

	def listen_task_info(self, task):
		self.__write_task_info(task)	

	def iterations_updated(self):
		pass
	
	def listen_found_new_commits(self,  new_commits_found, next_run_in_seconds ):
		idle_dict = {}
		idle_dict['new_commits_found'] = new_commits_found
		idle_dict['date'] = self.current_time()
		idle_dict['next_run_in_seconds']=next_run_in_seconds
		self._write_idle_info( str(idle_dict) )

	def listen_end_task_gently(self, task_name):
		"Ends task gently when a client aborts the execution, i.e, closes the logfile whith an 'END_TASK aborted' tuple"
		append_entry = "('END_TASK', '%s', '%s', 'Aborted'),\n" % (task_name, self.current_time())
		self._append_log_entry(append_entry)	
