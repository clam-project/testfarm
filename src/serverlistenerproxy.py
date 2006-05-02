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
	def __init__(self, client_name, service_url, repository_name) :
		self.iterations_needs_update = True
		self.client_name = client_name
		self.webservice = ServiceProxy(service_url)
		self.repository_name = repository_name
		
	def __append_log_entry(self, entry) :
		print self.webservice.remote_call(
			"append_log_entry", 
			repository_name=self.repository_name, 
			client_name=self.client_name, 
			entry=entry )

	def __write_idle_info(self, idle_info ):
		print self.webservice.remote_call(
			"write_idle_info",
			repository_name=self.repository_name, 
			client_name=self.client_name, 
			idle_info=idle_info )

	def current_time(self):
		return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

	def listen_result(self, command, ok, output, info, stats):
		entry = str( ('CMD', command, ok, output, info, stats) ) + ',\n'
		self.__append_log_entry(entry)

	def listen_begin_task(self, taskname):
		entry = "('BEGIN_TASK', '%s'),\n" % taskname 
		self.__append_log_entry(entry)

	def listen_end_task(self, taskname):
		entry = "('END_TASK', '%s'),\n" % taskname
		self.__append_log_entry(entry)
	
	def listen_begin_repository(self, repository_name):
		entry = "\n('BEGIN_REPOSITORY', '%s', '%s'),\n" % (repository_name, self.current_time())
		self.__append_log_entry(entry)
		self.iterations_needs_update = True

	def listen_end_repository(self, repository_name, status):
		entry = "('END_REPOSITORY', '%s', '%s', %s),\n" % (repository_name, self.current_time(), status)
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

