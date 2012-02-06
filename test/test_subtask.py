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

from task import *
from listeners import *
from coloredtest import ColoredTestCase
import os, os.path


def helperCurrentDir() :
	return os.path.abspath(os.curdir)

class Tests_SubTask(ColoredTestCase):
	def test_do_subtask__single_command_successful(self):
		subtask = SubTask("subtask", ["echo hello"])
		self.assertEquals(True, subtask.do_subtask())
	
	def test_do_subtask__multiple_command_successful(self):
		subtask = SubTask("subtask", ["echo hello", "ls"])
		self.assertEquals(True, subtask.do_subtask())
		
	def test_do_subtask__single_command_fails(self):
		subtask = SubTask("subtask", ["ls non-existing-file"])
		self.assertEquals(False, subtask.do_subtask())
		
	def test_do_subtask__multiple_command__one_fails(self):
		subtask = SubTask("subtask", ["ls", "ls non-existing-file", "echo hello"])
		self.assertEquals(False, subtask.do_subtask())

	## Results test
	def test_results_log__with_no_commands(self):
		subtask = SubTask("subtask name", [])
		listener = DummyResultListener()
		subtask.do_subtask( [listener] )
		self.assertEquals("""\
BEGIN_SUBTASK subtask name
END_SUBTASK subtask name""" , listener.log() )
	
	def test_results_log__single_command_ok(self):
		subtask = SubTask("subtask", ["echo hello"])
		listener = DummyResultListener()
		subtask.do_subtask( [listener] )
		self.assertEquals("""\
BEGIN_SUBTASK subtask
('echo hello', 'ok', '', '', {})
END_SUBTASK subtask""", listener.log() )
	
	def test_results_log__second_command_fails_so_exit(self):
		subtask = SubTask("subtask", ["echo hello", "non-existing-command", "ls"])
		listener = DummyResultListener()
		subtask.do_subtask( [listener] )
		self.assertEquals("""\
BEGIN_SUBTASK subtask
('echo hello', 'ok', '', '', {})
('non-existing-command', 'failure', '/bin/sh: non-existing-command: not found\\n', '', {})
END_SUBTASK subtask""", listener.log() )
	
	def test_results_log__command_fails_with_stderr_and_stdout(self):
		subtask = SubTask("subtask", ["./write_to_stderr_and_stdout.py"])
		listener = DummyResultListener()
		subtask.do_subtask( [listener] )
		self.assertEquals("""\
BEGIN_SUBTASK subtask
('./write_to_stderr_and_stdout.py', 'failure', 'ERR OUT\\n', '', {})
END_SUBTASK subtask""", listener.log() )
		
	def test_results_log__of_two_listeners(self):
		subtask = SubTask("subtask", ["echo hello"])
		listener1 = DummyResultListener()
		listener2 = DummyResultListener()
		subtask.do_subtask( [listener1, listener2] )
		self.assertEquals("""\
BEGIN_SUBTASK subtask
('echo hello', 'ok', '', '', {})
END_SUBTASK subtask""", listener1.log() )
		self.assertEquals("""\
BEGIN_SUBTASK subtask
('echo hello', 'ok', '', '', {})
END_SUBTASK subtask""", listener2.log() )
	
	def test_command_saves_changed_working_dir(self): #TODO make portable
		subtask = SubTask("subtaskcd", ["cd /tmp", "pwd > /tmp/foo"])
		subtask.do_subtask()
		self.assertEquals( "/tmp", open("/tmp/foo").read().strip() )
	
	def test_new_task_with_default_working_dir(self): #TODO make portable
		initial_directory = helperCurrentDir()
		subtask = SubTask("subtaskcd", ["cd /tmpXX"])
		subtask.do_subtask()
		self.assertEquals( initial_directory, helperCurrentDir() )
	
	# command map
	def test_info_parser(self):
		id = lambda text: text
		subtask = SubTask("subtask", [{CMD: "echo hello", INFO: id}])
		listener = DummyResultListener()
		subtask.do_subtask([listener])
		self.assertEquals( """\
BEGIN_SUBTASK subtask
('echo hello', 'ok', '', 'hello\\n', {})
END_SUBTASK subtask""", listener.log())

	def test_stats_parser(self):
		outlen = lambda text: {'len': len(text)} 
		subtask = SubTask("subtask", [{CMD: "echo hello", STATS: outlen}])
		listener = DummyResultListener()
		subtask.do_subtask([listener])
		self.assertEquals( """\
BEGIN_SUBTASK subtask
('echo hello', 'ok', '', '', {'len': 6})
END_SUBTASK subtask""", listener.log())

	def test_cd(self):
		id = lambda text: text
		previousdir= helperCurrentDir() 
		subtask = SubTask("subtask", [{CMD: 'pwd', INFO: id, CD: '/tmp'}])
		listener = DummyResultListener()
		subtask.do_subtask([listener])
		self.assertEquals( """\
BEGIN_SUBTASK subtask
('pwd', 'ok', '', '/tmp\\n', {})
END_SUBTASK subtask""", listener.log() )

	def test_status_ok(self):
		parseError = lambda text: not ('error' in text)
		previousdir= helperCurrentDir() 
		subtask = SubTask("subtask", [{CMD: 'echo error', STATUS_OK: parseError}])
		listener = DummyResultListener()
		subtask.do_subtask([listener])
		self.assertEquals( """\
BEGIN_SUBTASK subtask
('echo error', 'failure', 'error\\n', '', {})
END_SUBTASK subtask""", listener.log() )


