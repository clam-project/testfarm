import unittest
from testfarm import *
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
('non-existing-command', 'failure', 'sh: non-existing-command: command not found', '', {})
END_TASK task1
BEGIN_TASK task2
('echo foo', 'ok', '', '', {})
END_TASK task2
END_REPOSITORY repo name""", listener.log() )
