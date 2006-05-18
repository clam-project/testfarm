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


from service_proxy import ServiceProxy
import datetime

#
# Server Listener Proxy
#

class ServerListenerProxy:
	def __init__(self, client, service_url, project) : # TODO: control project and client if None
		self.iterations_needs_update = True
		self.client = client
		self.webservice = ServiceProxy(service_url)
		self.project = project
		self.__create_dirs()
		self.__write_project_info(self.project)
		self.__write_client_info(self.client)
	
	def __create_dirs(self):
		print self.webservice.remote_call(
			"create_dirs", 
			project_name=self.project.name) 
			
	def __append_log_entry(self, entry) :
		print '>>>>>>>>>>>>>>>>>>>> ', entry
		print self.webservice.remote_call(
			"append_log_entry", 
			project_name=self.project.name, 
			client_name=self.client.name, 
			entry=entry )

	def __write_idle_info(self, idle_info ):
		print self.webservice.remote_call(
			"write_idle_info",
			project_name=self.project.name, 
			client_name=self.client.name, 
			idle_info=idle_info )
			
	def __write_client_info(self, client):
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
			
			print self.webservice.remote_call(
				"write_client_info",
				client_name=self.client.name,
				project_name=self.project.name,
				client_info = entries) 

	def __write_project_info(self, project):# TODO : remove CODE DUPLICATION 
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

			print self.webservice.remote_call(
				"write_project_info",
				project_name=self.project.name,
				project_info=entries) 

	def current_time(self):
		return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

	def listen_end_command(self, command, ok, output, info, stats):
		entry = str( ('END_CMD', command, ok, output, info, stats) ) + ',\n'
		self.__append_log_entry('\t\t' + entry)

	def listen_begin_command(self, cmd):
		entry = "('BEGIN_CMD', '%s'),\n" % cmd 
		self.__append_log_entry('\t\t' + entry)

	def listen_begin_subtask(self, subtaskname):
		entry = "('BEGIN_SUBTASK', '%s'),\n" % subtaskname 
		self.__append_log_entry('\t' + entry)

	def listen_end_subtask(self, subtaskname):
		entry = "('END_SUBTASK', '%s'),\n" % subtaskname
		self.__append_log_entry(entry)
	
	def listen_begin_task(self, task_name):
		entry = "('BEGIN_TASK', '%s', '%s'),\n" % (task_name, self.current_time())
		self.__append_log_entry('\n' + entry)
		self.iterations_needs_update = True

	def listen_end_task(self, task_name, status):
		entry = "('END_TASK', '%s', '%s', '%s'),\n" % (task_name, self.current_time(), status)
		self.__append_log_entry(entry)
		self.iterations_needs_update = True

	def iterations_updated(self):
		self.iterations_needs_update = False
	
	def listen_found_new_commits(self,  new_commits_found, next_run_in_seconds ):
		idle_dict = {}
		idle_dict['new_commits_found'] = new_commits_found
		idle_dict['date'] = self.current_time()
		idle_dict['next_run_in_seconds']=next_run_in_seconds
		self.__write_idle_info( str(idle_dict) )

	def listen_end_task_gently(self, task_name):
		append_entry = "('END_TASK', '%s', '%s', 'Aborted'),\n" % (task_name, self.current_time())
		self.__append_log_entry(append_entry)	
