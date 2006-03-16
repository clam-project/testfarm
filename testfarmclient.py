import commands
import os
from listeners import NullResultListener, ConsoleResultListener

class TestFarmClient :
	# Attributes : repositories[]
	
	def __init__(self, repositories=[], listeners=[ ConsoleResultListener() ]) :
		self.repositories = repositories
		self.listeners = listeners
		for repo in self.repositories :
			repo.do_tasks( self.listeners )
		
	def num_repositories(self) :
		return len( self.repositories )


def get_command_and_parsers(maybe_dict):
	info_parser = None
	stats_parser = None
	status_ok_parser = None 
	try:
		cmd = 'echo no explicit command provided'
		if maybe_dict.has_key(CMD) :
			cmd = maybe_dict[CMD] 
		if maybe_dict.has_key(INFO) :
			info_parser = maybe_dict[INFO]
		if maybe_dict.has_key(STATS) :
			stats_parser = maybe_dict[STATS]
		if maybe_dict.has_key(CD) :
			destination_dir = maybe_dict[CD]
			os.chdir( destination_dir )
		if maybe_dict.has_key(STATUS_OK) :
			status_ok_parser = maybe_dict[STATUS_OK]
	except AttributeError:
		cmd = maybe_dict
	return (cmd, info_parser, stats_parser, status_ok_parser)

class Task:
	def __init__(self, name, commands):
		self.name = name
		self.commands = commands

	def __begin_task(self, listeners):
		for listener in listeners :
			listener.listen_begin_task( self.name )

	def __end_task(self, listeners):
		for listener in listeners :
			listener.listen_end_task( self.name )
	
	def __send_result(self, listeners, cmd, status, output, info, stats):		
		for listener in listeners :
			listener.listen_result( cmd, status, output, info, stats )


	def do_task(self, listeners = [ NullResultListener() ] ):
		self.__begin_task(listeners)
		initial_working_dir = os.path.abspath(os.curdir)
		for maybe_dict in self.commands :
			cmd, info_parser, stats_parser, status_ok_parser = get_command_and_parsers(maybe_dict)
			temp_file = "%s/current_dir.temp" % initial_working_dir #TODO multiplatform
			cmd_with_pwd = cmd + " && pwd > %s" % temp_file
			exit_status, output = commands.getstatusoutput(cmd_with_pwd)
			if status_ok_parser :
				status_ok = status_ok_parser( output ) #TODO assert that returns a boolean
			else:
				status_ok = (exit_status == 0)
			if info_parser :
				info = info_parser(output)
			else :
				info = ''
			if stats_parser :
				stats = stats_parser(output)
			else:
				stats = {}
			if status_ok :
				output = ''
			self.__send_result(listeners, cmd, status_ok, output, info, stats)
			current_dir = open( temp_file ).read().strip()
			os.chdir( current_dir )
			if not status_ok :
				self.__end_task(listeners)
				os.chdir ( initial_working_dir )
				return False
		self.__end_task(listeners)
		os.chdir ( initial_working_dir )
		return True

class Repository :
	# Attributes : name, tasks[], deployment_task[] 

	def __init__(self, name = '-- unnamed repository --'): 
		self.name = name;
		self.tasks = []
		self.deployment_task = None
		
	def get_name(self):
		return self.name;
		
	def get_num_tasks(self): # Note : Deployment task is considered as a separated task
		return len( self.tasks )
	
	def add_deployment_task(self, commands):
		self.add_task("Deployment Task", commands)

	def add_task(self, taskname, commands):
		self.tasks.append(Task(taskname, commands)) 
	
	def do_tasks( self, listeners = [ NullResultListener() ] ):
		all_ok = True
		for listener in listeners:
			listener.listen_begin_repository( self.name )
		for task in self.tasks :
			current_result = task.do_task(listeners)
			all_ok = all_ok and current_result
		for listener in listeners:
			listener.listen_end_repository( self.name, all_ok )
		return all_ok
CMD = 1
INFO = 2
STATS = 3
CD = 4
STATUS_OK = 5
