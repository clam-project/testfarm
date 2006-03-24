from service_proxy import ServiceProxy
import datetime

#
# Server Listener Proxy
#

class ServerListenerProxy:
	def __init__(self, 
		client_name='testing_client', 
		service_url = "http://10.55.0.66/testfarm_server"
	) :
		self.iterations_needs_update = True
		self.client_name = client_name
		self.webservice = ServiceProxy(service_url)
		
	def __append_log_entry(self, entry) :
		print self.webservice.remote_call(
			"append_log_entry", 
			client_name=self.client_name, 
			entry=entry )

	def __write_idle_info(self, idle_info ):
		print self.webservice.remote_call(
			"write_idle_info", 
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
	
	def listen_begin_repository(self, repositoryname):
		entry = "\n('BEGIN_REPOSITORY', '%s', '%s'),\n" % (repositoryname, self.current_time())
		self.__append_log_entry(entry)
		self.iterations_needs_update = True

	def listen_end_repository(self, repositoryname, status):
		entry = "('END_REPOSITORY', '%s', '%s', %s),\n" % (repositoryname, self.current_time(), status)
		self.__append_log_entry(entry)
		self.iterations_needs_update = True

	def iterations_updated(self):
		self.iterations_needs_update = False
	
	def listen_found_new_commits(self, new_commits_found, next_run_in_seconds ):
		idle_dict = {}
		idle_dict['new_commits_found'] = new_commits_found
		idle_dict['date'] = self.current_time()
		idle_dict['next_run_in_seconds']=next_run_in_seconds
		self.__write_idle_info( str(idle_dict) )

