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

import unittest
from testfarmclient import *
from listeners import DummyResultListener

class Tests_Repository(unittest.TestCase):

	def test_name(self):
		repository = Repository('reponame') 
		self.assertEquals('reponame', repository.get_name())
		
	def test_name__default_consructor(self):
		repository = Repository()
		self.assertEquals('-- unnamed repository --', repository.get_name())

	def test_num_tasks_default(self):
		repository = Repository('reponame1')
		self.assertEquals(0, repository.get_num_tasks())
	
	def test_num_tasks_multiple(self):
		repository = Repository('reponame2')
		repository.add_task( "taskname1" , [] )
		repository.add_task( "taskname2" , [] )
	
		self.assertEquals(2, repository.get_num_tasks())

	def test_num_tasks_multiple__with_deployment_task(self):
		repository = Repository()
		repository.add_deployment_task( [] )
		repository.add_task( "taskname1" , [] )
	
		self.assertEquals(2, repository.get_num_tasks())

	def test_do_tasks__single_task_successful(self):
		repository = Repository()
		repository.add_task( "taskname" , ["echo hello"] )
		
		self.assertEquals(True, repository.do_tasks())
	
	def test_do_tasks__multiple_task_last_fails(self):
		repository = Repository()
		repository.add_task( "taskname" , 
			["echo hello", "non-existing-command"] )
		
		self.assertEquals(False, repository.do_tasks())


	# Results Tests
	def test_results_log__repository_default(self):
		repository = Repository("repo name")
		listener = DummyResultListener()
		repository.do_tasks([listener])
		self.assertEquals( """\
BEGIN_REPOSITORY repo name
END_REPOSITORY repo name""", listener.log() )

	def test_results_log__two_tasks_first_fails(self):
		repository = Repository("repo name")
		repository.add_task("task1", ["non-existing-command"])
		repository.add_task("task2", ["echo foo"])
		listener = DummyResultListener()
		repository.do_tasks([listener])
		self.assertEquals(  """\
BEGIN_REPOSITORY repo name
BEGIN_TASK task1
('non-existing-command', 'failure', '/bin/sh: non-existing-command: command not found\\n', '', {})
END_TASK task1
BEGIN_TASK task2
('echo foo', 'ok', '', '', {})
END_TASK task2
END_REPOSITORY repo name""", listener.log() )

	def test_mandatory_task(self):
		repo = Repository('repo')	
		repo.add_task('task1', ["echo task1"])	
		repo.add_mandatory_task('task2', ["echo something echoed", "lsss gh"])
		repo.add_task('task3', ["echo task3"])	
		listener = DummyResultListener()
		repo.do_tasks([listener])
		self.assertEquals("""\
BEGIN_REPOSITORY repo
BEGIN_TASK task1
('echo task1', 'ok', '', '', {})
END_TASK task1
BEGIN_TASK task2
('echo something echoed', 'ok', '', '', {})
('lsss gh', 'failure', '/bin/sh: lsss: command not found\\n', '', {})
END_TASK task2
END_REPOSITORY repo""", listener.log() )
