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

import commands, os, time, sys, subprocess, tempfile

from listeners import NullResultListener, MultiListener, ConsoleResultListener
import mail

def is_string( data ):
	try: # TODO : find another clean way to tho this check
		data.isalpha()
		return True
	except AttributeError:
		return False

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
		if maybe_dict.has_key(CD) : # TODO : maybe remove
			destination_dir = maybe_dict[CD]
			os.chdir( destination_dir )
		if maybe_dict.has_key(STATUS_OK) :
			status_ok_parser = maybe_dict[STATUS_OK]
	except AttributeError:
		cmd = maybe_dict
	return (cmd, info_parser, stats_parser, status_ok_parser)


def run_command_with_log(command, verbose = True, logfilename = None, write_as_html = False):

	if verbose and logfilename:
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
			if verbose and logFile:
				logFile.write(tmp)
				logFile.flush()
		if pipe.poll() is not None:
			for line in pipe.stdout :
				output.append(line)
			break
	status = pipe.wait()

	if verbose and logFile:
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


class SubTask:
	"Defines a subtask, with a set of commands"
	def __init__(self, name, commands, mandatory = False):
		self.name = name
		self.commands = commands
		self.mandatory = mandatory

	def is_mandatory(self):
		"Returns if the subtask is mandatory or not"
		return self.mandatory

	def do_subtask(self, listener, server_to_push = None, verbose=False): #TODO : Refactor
		"Executes the subtask and all its commands"

		listener.listen_begin_subtask( self.name )
		if server_to_push:
			server_to_push.update_static_html_files()
		initial_working_dir = os.path.abspath(os.curdir)
		temp_file = tempfile.NamedTemporaryFile()
		temp_file_name = temp_file.name
		if sys.platform =='win32':
			temp_file_name = 'C:\\testfarmtemp.txt'
		for command_definition in self.commands :
			# 1 : Create a temp file to save working directory
			cmd, info_parser, stats_parser, status_ok_parser = get_command_and_parsers(command_definition)
			pwd_cmd = 'pwd'
			if sys.platform == 'win32' : pwd_cmd = 'cd'
			cmd_with_pwd = cmd + " && %s > '%s'" %(pwd_cmd, temp_file_name)
			# 2 : Begin command run
			listener.listen_begin_command( cmd )
			if server_to_push: #TODO
				server_to_push.update_static_html_files()
			output, exit_status = run_command(cmd_with_pwd, initial_working_dir, verbose=verbose)

			status_ok = status_ok_parser( output ) if status_ok_parser else (exit_status==0)
			info  = info_parser(output)  if info_parser  else ''
			stats = stats_parser(output) if stats_parser else {}
			if status_ok : output = ''

			f = open( temp_file_name )
			current_dir = f.read().strip()
			f.close()

			if not status_ok :
				os.chdir ( initial_working_dir )
				listener.listen_end_command( cmd, status_ok, output, info, stats )
				listener.listen_end_subtask( self.name )
				temp_file.close()
				return False
			# 3: End command run
			os.chdir ( initial_working_dir )
			listener.listen_end_command( cmd, status_ok, output, info, stats )
			if server_to_push: #TODO
				server_to_push.update_static_html_files()
			if current_dir:
				os.chdir( current_dir )
		os.chdir ( initial_working_dir )
		listener.listen_end_subtask( self.name )
		temp_file.close()
		return True

class Task :
	# Attributes : name, subtasks[], deployment[]
	"Defines a task, with a set of subtasks"
	def __init__(self, project, client, task_name = '-- unnamed task --'):
		self.name = task_name;
		assert is_string(project.name), '< %s > is not a valid project name (should be a string)' % str(project_name)
		self.project = project
		assert is_string(client.name), '< %s > is not a valid client name (should be a string)' % str(client_name)
		self.client = client
		self.subtasks = []
		self.deployment = None #TODO : use this as unique development task
		self.not_idle_checking_cmd = ""
		self.seconds_idle = 0
		self.last_commiter=""
		self.last_revision=""
		self.repositories_to_check = []
		self.repositories = []

	def get_name(self):
		return self.name;

	def get_num_subtasks(self): # Note : Deployment task is considered as a separated task
		return len( self.subtasks )

	def set_check_for_new_commits(self, checking_cmd, minutes_idle = 5 ):
		"Sets the checking command and seconds to idle"
		self.not_idle_checking_cmd = checking_cmd
		self.seconds_idle = minutes_idle * 60

	def set_repositories_to_keep_state_of(self, repositories):
		self.repositories_to_check = repositories

	def add_deployment(self, commands): #TODO must be unique
		"A separated subtask to deploy"
		self.add_subtask("Deployment", commands, mandatory = True)

	def add_subtask(self, subtaskname, commands, mandatory = False):
		"Adds a subtask"
		self.subtasks.append(SubTask(subtaskname, commands, mandatory))

	def do_checking_for_new_commits(self, listeners, verbose=False):
		"Checks if there is a new commit in the version control system"
		listener = MultiListener(listeners)
		initial_working_dir = os.path.abspath(os.curdir)
		if not self.not_idle_checking_cmd :
			new_commits_found = True #default
		else :
			output, zero_if_new_commits_found = run_command( self.not_idle_checking_cmd, initial_working_dir, verbose=verbose )
			new_commits_found = not zero_if_new_commits_found

		if new_commits_found :
			#TODO solve how to chdir to clam
			for repos in self.repositories_to_check:
				cdclam = "cd ~/%s && " % repos
				committer, _ =  run_command(
					cdclam+"svn info -rHEAD | grep Author: | while read a b c d; do echo $d; done", initial_working_dir )
				last_committer = committer.strip()
				revision, _ = run_command(
					cdclam+"svn info -rHEAD | grep Rev: | while read a b c d; do echo $d; done", initial_working_dir )
				last_revision = revision.strip()
				if len(last_revision.split())>1 :
					# svn command was error
					last_commiter=""
					last_revision=""
				print repos, last_revision, last_committer
				self.repositories.append((repos, last_revision, last_committer))

		listener.listen_found_new_commits( new_commits_found, self.seconds_idle )

		return new_commits_found

	def do_subtasks( self, listeners = [ NullResultListener() ], server_to_push = None, verbose=False):
		"Executes all subtasks and sends results"
		listener = MultiListener(listeners)
		all_ok = True
		failed_subtasks = []
		listener.listen_task_info(self)
		listener.listen_begin_task( self.name, self.repositories )
		for subtask in self.subtasks :
			subtask_ok = subtask.do_subtask(listener, server_to_push, verbose=verbose)
			all_ok = all_ok and subtask_ok
			if not subtask_ok and subtask.is_mandatory() : # if it is a failing mandatory task, force the end of repository
				break
			if not subtask_ok :
				failed_subtasks.append(subtask.name) # TODO
			if server_to_push :
				server_to_push.update_static_html_files()
		listener.listen_end_task( self.name, all_ok )
		if server_to_push :
			server_to_push.update_static_html_files()

		return all_ok

	def stop_execution_gently(self, listeners = [], server_to_push = None): # TODO : Refactor, only for ServerListener
		"Asks listeners to stop the task execution gently if the execution was aborted by user"
		listener = MultiListener(listeners)
		listener.listen_end_task_gently(self.name)
		if server_to_push :
			server_to_push.update_static_html_files()

CMD = 1
INFO = 2
STATS = 3
CD = 4
STATUS_OK = 5
