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

import commands, os, time, sys, subprocess

from listeners import NullResultListener, ConsoleResultListener
from testfarmserver import * 
from serverlistenerproxy import ServerListenerProxy

def is_string( data ):
	try: # TODO : find another clean way to tho this check 
		data.isalpha()
		return True
	except AttributeError:
		return False
	
class TestFarmClient :
	def __init__(self, 
		name,
		repository,
		continuous=False,
		html_base_dir = None,
		logs_base_dir='/tmp/testfarm_logs',
		remote_server_url = None,
		verbose = False,
		testinglisteners = []

	) :
		assert is_string(name), '< %s > is not a valid client name (should be a string)' % str(name)
		self.name = name

		self.listeners = [ ConsoleResultListener() ]

		serverlistener = None # for keyboard interrupt purpose

		if remote_server_url:
			listenerproxy = ServerListenerProxy(
				client_name=name, 
				service_url=remote_server_url,
				repository_name=repository.name
			)		
			self.listeners.append( listenerproxy )
		if html_base_dir :	
			serverlistener = ServerListener( 
				client_name=self.name, 
				logs_base_dir=logs_base_dir,
				repository_name=repository.name
			)
			self.listeners.append( serverlistener )
			server_to_push = TestFarmServer( 
				logs_base_dir=logs_base_dir, 
				html_base_dir=html_base_dir, 
				repository_name=repository.name )

		else:
			server_to_push = None

		if testinglisteners:
			self.listeners = testinglisteners

		try :
			#do_tasks at lease one time	
			repository.do_checking_for_new_commits( self.listeners, verbose=verbose ) #this creates a valid .idle file
			repository.do_tasks( self.listeners, server_to_push = server_to_push, verbose=verbose )

			while continuous :
				new_commits_found = repository.do_checking_for_new_commits( self.listeners, verbose=verbose )
				if new_commits_found:
					repository.do_tasks( self.listeners, server_to_push = server_to_push, verbose=verbose )
				else:
					if server_to_push: #update idle time display
						server_to_push.update_static_html_files()
					time.sleep( repository.seconds_idle )
		except KeyboardInterrupt :
			print "Keyboard Interrupt. Stopping execution gently"
			if serverlistener :
				repository.stop_execution_gently([serverlistener], server_to_push = server_to_push)
		

def get_command_and_parsers(maybe_dict):
	info_parser = None
	stats_parser = None
	status_ok_parser = None 
	try:
		cmd = 'echo no command specified'
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


def run_command_with_log(command, verbose = True, logfilename = None, write_as_html = False):

	if logfilename:
		logFile = open(logfilename, "a")
		if write_as_html:
			logFile.write("<hr/>")
			logFile.write("<p><span style=\"color:red\">command</span>: %s</p>" % command)
			logFile.write("<p><span style=\"color:red\">output</span>:</p><pre>\n")
		else:
			logFile.write("-" * 60 + "\n")
			logFile.write("command: %s\n" % command)
			logFile.write("output:\n")
		logFile.flush()
	else:
		logFile = None
	
	output = []
	 
	pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	  
	while True:
		tmp = pipe.stdout.readline()
		
		output.append( tmp )
		
		if tmp:
			if verbose:
				print tmp.strip()
						
			if logFile:
				logFile.write(tmp)
				logFile.flush()
							
		if pipe.poll() is not None:
			break
	
	status = pipe.wait()
	
	if logFile:
		if write_as_html:
			logFile.write("</pre><p><span style=\"color:red\">status</span>: %d</p>" % status)
		else:
			logFile.write("status: %d\n" % status)
		logFile.flush()
		logFile.close()
	
	return (''.join(output), status)
	
	
def run_command(command, initial_working_dir, verbose=False):
	logfile = initial_working_dir + "/command_log.html"
	return run_command_with_log(command, verbose=verbose, logfilename=logfile, write_as_html=True)


class Task:
	def __init__(self, name, commands, mandatory = False):
		self.name = name
		self.commands = commands
		self.mandatory = mandatory

	def __begin_task(self, listeners):
		for listener in listeners :
			listener.listen_begin_task( self.name )

	def __end_task(self, listeners):
		for listener in listeners :
			listener.listen_end_task( self.name )
	
	def __send_result(self, listeners, cmd, status, output, info, stats):		
		for listener in listeners :
			listener.listen_result( cmd, status, output, info, stats )

	def is_mandatory(self):
		return self.mandatory

	def do_task(self, listeners = [ NullResultListener() ] , server_to_push = None, verbose=False):
		self.__begin_task(listeners)
		if server_to_push:
				server_to_push.update_static_html_files()
		initial_working_dir = os.path.abspath(os.curdir)
		for maybe_dict in self.commands :
			cmd, info_parser, stats_parser, status_ok_parser = get_command_and_parsers(maybe_dict)
			temp_file = "%s/current_dir.temp" % initial_working_dir #TODO multiplatform
			if sys.platform == 'win32':
				cmd_with_pwd = cmd + " && cd > %s" % temp_file
			else:
				cmd_with_pwd = cmd + " && pwd > %s" % temp_file
			output, exit_status = run_command(cmd_with_pwd, initial_working_dir, verbose=verbose)
			if status_ok_parser :
				status_ok = status_ok_parser( output ) #TODO assert that returns a boolean
			else:
				status_ok = exit_status == 0
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
			if False and server_to_push: #TODO
				server_to_push.update_static_html_files()
			current_dir = open( temp_file ).read().strip()
			if current_dir:
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
		self.not_idle_checking_cmd = ""
		self.seconds_idle = 0
		
	def get_name(self):
		return self.name;
		
	def get_num_tasks(self): # Note : Deployment task is considered as a separated task
		return len( self.tasks )
	
	def add_checking_for_new_commits(self, checking_cmd, minutes_idle = 5 ):
		self.not_idle_checking_cmd = checking_cmd
		self.seconds_idle = minutes_idle * 60

	def add_deployment_task(self, commands): #TODO abort if fails
		self.add_task("Deployment Task", commands)

	def add_task(self, taskname, commands):
		self.tasks.append(Task(taskname, commands))

	def add_mandatory_task(self, taskname, commands):
		self.tasks.append(Task(taskname, commands, mandatory = True))

	def do_checking_for_new_commits(self, listeners, verbose=False):
		initial_working_dir = os.path.abspath(os.curdir)
		if not self.not_idle_checking_cmd :
			new_commits_found = True #default
		else :
			output, zero_if_new_commits_found = run_command( self.not_idle_checking_cmd, initial_working_dir, verbose=verbose )
			new_commits_found = not zero_if_new_commits_found
		for listener in listeners :
			listener.listen_found_new_commits( new_commits_found, self.seconds_idle )
		return new_commits_found

	def do_tasks( self, listeners = [ NullResultListener() ], server_to_push = None, verbose=False): 
		all_ok = True
		for listener in listeners:
			listener.listen_begin_repository( self.name )
		for task in self.tasks :
			current_result = task.do_task(listeners, server_to_push, verbose=verbose)
			all_ok = all_ok and current_result
			print "current result => ", current_result, "task is mandatory ? => ", task.is_mandatory()			
			if not current_result and task.is_mandatory() : # if it is a failing mandatory task, force the end of repository  
				break 
			if server_to_push : #TODO remove. this is just provisional. Is it?
				server_to_push.update_static_html_files()
		for listener in listeners:
			listener.listen_end_repository( self.name, all_ok )
		if server_to_push : #TODO remove. this is just provisional. Is it?
			server_to_push.update_static_html_files()
		return all_ok

	def stop_execution_gently(self, listeners = [], server_to_push = None): # TODO : Refactor, only for ServerListener
		for listener in listeners:
			listener.listen_stop_repository_gently()
		if server_to_push :
			server_to_push.update_static_html_files()
		pass 

CMD = 1
INFO = 2
STATS = 3
CD = 4
STATUS_OK = 5
