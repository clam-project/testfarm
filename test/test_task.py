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
from coloredtest import ColoredTestCase
from listeners import DummyResultListener
from client import Client
from project import Project

class Tests_Task(ColoredTestCase):

	def test_name(self):
		a_project = Project('project name')
		a_client = Client('client name')
		task = Task(a_project, a_client,'taskname') 
		self.assertEquals('taskname', task.get_name())
		
	def test_name__default_consructor(self):
		a_project = Project('project name')
		a_client = Client('client name')
		task = Task(a_project, a_client) 
		self.assertEquals('-- unnamed task --', task.get_name())

	def test_num_subtasks_default(self):
		a_project = Project('project name')
		a_client = Client('client name')
		task = Task(a_project, a_client,'taskname1') 
		self.assertEquals(0, task.get_num_subtasks())
	
	def test_num_subtasks_multiple(self):
		a_project = Project('project name')
		a_client = Client('client name')
		task = Task(a_project, a_client,'taskname2') 
		task.add_subtask( "subtaskname1" , [] )
		task.add_subtask( "subtaskname2" , [] )
	
		self.assertEquals(2, task.get_num_subtasks())

	def test_num_subtasks_multiple__with_deployment_task(self):
		a_project = Project('project name')
		a_client = Client('client name')
		task = Task(a_project, a_client) 
		task.add_deployment( [] )
		task.add_subtask( "subtaskname1" , [] )
	
		self.assertEquals(2, task.get_num_subtasks())

	def test_do_subtasks__single_subtask_successful(self):
		a_project = Project('project name')
		a_client = Client('client name')
		task = Task(a_project, a_client) 
		task.add_subtask( "subtaskname" , ["echo hello"] )
		
		self.assertEquals(True, task.do_subtasks())
	
	def test_do_subtasks__multiple_subtask_last_fails(self):
		a_project = Project('project name')
		a_client = Client('client name')
		task = Task(a_project, a_client) 
		task.add_subtask( "subtaskname" , 
			["echo hello", "non-existing-command"] )
		
		self.assertEquals(False, task.do_subtasks())


	# Results Tests
	def test_results_log__task_default(self):
		a_project = Project('project name')
		a_client = Client('client name')
		task = Task(a_project, a_client,'task name') 
		listener = DummyResultListener()
		task.do_subtasks([listener])
		self.assertEquals( """\
BEGIN_TASK task name
END_TASK task name""", listener.log() )

	def test_results_log__two_subtasks_first_fails(self):
		a_project = Project('project name')
		a_client = Client('client name')
		task = Task(a_project, a_client,'task name') 
		task.add_subtask("subtask1", ["non-existing-command"])
		task.add_subtask("subtask2", ["echo foo"])
		listener = DummyResultListener()
		task.do_subtasks([listener])
		self.assertEquals(  """\
BEGIN_TASK task name
BEGIN_SUBTASK subtask1
('non-existing-command', 'failure', '/bin/sh: non-existing-command: command not found\\n', '', {})
END_SUBTASK subtask1
BEGIN_SUBTASK subtask2
('echo foo', 'ok', '', '', {})
END_SUBTASK subtask2
END_TASK task name""", listener.log() )

	def test_mandatory_subtask(self):
		a_project = Project('project name')
		a_client = Client('client name')
		task = Task(a_project, a_client,'task') 
		task.add_subtask('subtask1', ["echo subtask1"])	
		task.add_subtask('subtask2', ["echo something echoed", "lsss gh"], mandatory = True)
		task.add_subtask('subtask3', ["echo subtask3"])	
		listener = DummyResultListener()
		task.do_subtasks([listener])
		self.assertEquals("""\
BEGIN_TASK task
BEGIN_SUBTASK subtask1
('echo subtask1', 'ok', '', '', {})
END_SUBTASK subtask1
BEGIN_SUBTASK subtask2
('echo something echoed', 'ok', '', '', {})
('lsss gh', 'failure', '/bin/sh: lsss: command not found\\n', '', {})
END_SUBTASK subtask2
END_TASK task""", listener.log() )


