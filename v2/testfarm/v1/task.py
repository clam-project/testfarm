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

import os, time, sys, subprocess, tempfile
from listeners import NullResultListener, MultiListener, ConsoleResultListener
import testfarm.utils as utils

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


def run_command(command, verbose=False):
	log = utils.buffer()
	out = log
	error = utils.quotedFile(log, "\033[31m", "\033[0m")
	message=''
	if verbose:
		message = "Running: '%s'"%command
		out = utils.tee(log, sys.stdout)
		error = utils.tee(error, sys.stderr)

	ok = utils.run(command, log=out, err=error, fatal=False, message=message)
	return log.output(), ok


class SubTask:
	"Defines a subtask, with a set of commands"
	def __init__(self, name, commands, mandatory = False):
		self.name = name
		self.commands = commands
		self.mandatory = mandatory

	def is_mandatory(self):
		"Returns if the subtask is mandatory or not"
		return self.mandatory

	def do_subtask(self, listener, verbose=False): #TODO : Refactor
		"Executes the subtask and all its commands"

		listener.listen_begin_subtask( self.name )
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
			output, command_ok = run_command(cmd_with_pwd, verbose=verbose)

			status_ok = status_ok_parser( output ) if status_ok_parser else command_ok
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
		self.changes = []
		self.sandboxes = []

	# Deprecated: use add_sandbox with an XSandbox object
	def set_repositories_to_keep_state_of(self, sandboxes):
		#TODO supposes that sandboxes are in ~!!!
		from SvnSandbox import SvnSandbox
		for repo in sandboxes :
			self.sandboxes.append(SvnSandbox("~/%s"%repo))

	def add_sandbox(self, sandbox) :
		self.sandboxes.append(sandbox)

	def get_name(self):
		return self.name;

	def get_num_subtasks(self): # Note : Deployment task is considered as a separated task
		return len( self.subtasks )

	def set_check_for_new_commits(self, checking_cmd, minutes_idle = 5 ):
		"Sets the checking command and seconds to idle"
		self.not_idle_checking_cmd = checking_cmd
		self.seconds_idle = minutes_idle * 60

	def add_deployment(self, commands): #TODO must be unique
		"A separated subtask to deploy"
		self.add_subtask("Deployment", commands, mandatory = True)

	def add_subtask(self, subtaskname, commands, mandatory = False):
		"Adds a subtask"
		self.subtasks.append(SubTask(subtaskname, commands, mandatory))

	def _has_new_commits(self, verbose) :
		if self.not_idle_checking_cmd and not self.sandboxes :
			# No way of knowing whether has new commits, suppose always needs to be run
			return True
		# TODO: early return
		new_commits_found = False
		if self.not_idle_checking_cmd :
			output, has_changes = run_command( self.not_idle_checking_cmd, verbose=verbose )
			if has_changes :
				print "Pending commits found"
				new_commits_found = True
		for sandbox in self.sandboxes :
			if sandbox.hasPendingChanges() :
				print "Dirty: ", sandbox.sandbox
				new_commits_found = True
		return new_commits_found

	def do_checking_for_new_commits(self, listeners, verbose=False):
		"Checks if there is a new commit in the version control system"
		listener = MultiListener(listeners)

		if not self._has_new_commits(verbose) :
			listener.listen_found_new_commits( False, self.seconds_idle )
			return False

		for sandbox in self.sandboxes :
			for author, revision, msg in sandbox.guilty() :
				self.changes.append(
					(os.path.basename(sandbox.sandbox), revision, author))
				print os.path.basename(sandbox.sandbox), revision, author

		listener.listen_found_new_commits( True, self.seconds_idle )
		return True

	def do_subtasks( self, listeners = [ NullResultListener() ], verbose=False):
		"Executes all subtasks and sends results"
		listener = MultiListener(listeners)
		all_ok = True
		failed_subtasks = []
		listener.listen_task_info(self)
		listener.listen_begin_task( self.name, self.changes )
		if self.sandboxes :
			sub_task_name = "Update Sandbox"
			listener.listen_begin_subtask(sub_task_name)
			for sandbox in self.sandboxes :
				fake_command = "Change log for %s"%sandbox.location()
				listener.listen_begin_command(fake_command)
				output = ''.join([
					":: %s - %s\n%s\n\n"%(revision, author, message)
					for revision, author, message in sandbox.guilty()])
				listener.listen_end_command(fake_command, True, '', output, {})
			for sandbox in self.sandboxes :
				fake_command = "Updating %s, %s -> %s"%(
					sandbox.location(),
					sandbox.state(),
					sandbox.remoteState(),
					)
				listener.listen_begin_command(fake_command)
				sandbox.update()
				listener.listen_end_command(fake_command, True, '', '', {})
			listener.listen_end_subtask(sub_task_name)

		for subtask in self.subtasks :
			subtask_ok = subtask.do_subtask(listener, verbose=verbose)
			all_ok = all_ok and subtask_ok
			if not subtask_ok and subtask.is_mandatory() : # if it is a failing mandatory task, force the end of repository
				break
			if not subtask_ok :
				failed_subtasks.append(subtask.name) # TODO
		listener.listen_end_task( self.name, all_ok )

		return all_ok

	def stop_execution_gently(self, listeners = []): # TODO : Refactor, only for ServerListener
		"Asks listeners to stop the task execution gently if the execution was aborted by user"
		listener = MultiListener(listeners)
		listener.listen_end_task_gently(self.name)

CMD = 1
INFO = 2
STATS = 3
CD = 4
STATUS_OK = 5
