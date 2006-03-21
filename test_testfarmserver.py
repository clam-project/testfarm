import unittest
import datetime
from listeners import *
from testfarmclient import *
from testfarmserver import *

class ColoredTestCase(unittest.TestCase):
	def assertEquals(self, expected, result):
		if expected == result :
			return
		expectedstr = str(expected)
		resultstr = str(result)
		red = "\x1b[31;01m"
		green ="\x1b[32;01m"
		yellow = "\x1b[33;01m" # unreadable on white backgrounds
		cyan = "\x1b[36;01m"
		normal = "\x1b[0m"

		index_diff = 0
		for i in range(len(resultstr)):
			if expectedstr[i]!=resultstr[i]:
				index_diff = i
				break
		print "\n<expected>%s%s%s%s%s</expected>" % (cyan, expectedstr[:index_diff], green, expectedstr[index_diff:], normal)
		print "\n<but was>%s%s%s%s%s</but was>" % (cyan, resultstr[:index_diff], red, resultstr[index_diff:], normal)
		
		assert False, "different strings"

class Tests_TestFarmServer(ColoredTestCase):
	def test_iterations__one_green_iteration(self):
		listener = ServerListener()
		listener.current_time = lambda : "a date"
		server = TestFarmServer()
		repo = Repository('repo')	
		repo.add_task('task1', [])	
		TestFarmClient('a client', [repo],[listener])
		self.assertEquals(
			{'testing_client' : [('a date', 'a date', 'repo', 'stable')]}, 
			server.iterations() )

	def test_details(self):
		listener = ServerListener( client_name='a client')
		server = TestFarmServer()
		listener.current_time = lambda : "2004-03-17-13-26-20"
		listener.listen_begin_repository("not wanted")
		listener.listen_begin_task("task")
		listener.listen_end_task("task")
		listener.listen_end_repository("name", False)
		listener.current_time = lambda : "1999-99-99-99-99-99"
		listener.listen_begin_repository("we want this one")
		listener.listen_begin_task("task")
		listener.listen_result("a command", False, "", "some info", {'a':1})
		listener.listen_end_task("task")
		listener.current_time = lambda : "2000-00-00-00-00-00"
		listener.listen_end_repository("we want this one", False)
		listener.current_time = lambda : "2005-03-17-13-26-20"
		listener.listen_begin_repository("not wanted either")
		listener.listen_begin_task("task")
		listener.listen_end_task("task")
		listener.listen_end_repository("name", False)
		expected = [
('BEGIN_REPOSITORY', 'we want this one', '1999-99-99-99-99-99'),
('BEGIN_TASK', 'task'),
('CMD', 'a command', False, '', 'some info', {'a':1}),
('END_TASK', 'task'),
('END_REPOSITORY', 'we want this one', '2000-00-00-00-00-00', False),
]
		self.assertEquals( expected, server.single_iteration_details('a client', '1999-99-99-99-99-99') )

	def test_two_clients(self):
		listener1 = ServerListener(client_name='client 1', logs_base_dir='/tmp/clients_testdir')
		listener2 = ServerListener(client_name='client 2', logs_base_dir='/tmp/clients_testdir')
		listener1.clean_log_files()
		listener2.clean_log_files()
		listener1.current_time = lambda : "some date"
		listener2.current_time = lambda : "some other date"
		server = TestFarmServer(logs_base_dir='/tmp/clients_testdir')
		repo = Repository('repo')
		repo.add_task('task1', [])
		TestFarmClient('a client', [repo], [listener1])
		TestFarmClient('another client', [repo], [listener2])
		self.assertEquals( 
			{'client 1':[('some date', 'some date', 'repo', 'stable')],
			 'client 2':[('some other date', 'some other date', 'repo', 'stable')]}, 
			server.iterations() )
		listener1.clean_log_files()
		listener2.clean_log_files()

	def tearDown(self):
		listener = ServerListener()
		listener.clean_log_files()

	def setUp(self):
		listener = ServerListener()
		listener.clean_log_files()

class Tests_ServerListener(ColoredTestCase):

	def tearDown(self):
		listener = ServerListener()
		listener.clean_log_files()

	def setUp(self):
		listener = ServerListener()
		listener.clean_log_files()

	def test_multiple_repositories_multiple_tasks(self):
		id = lambda txt : txt
		listener = ServerListener()
		listener.current_time = lambda : "2006-03-17-13-26-20"
		repo1 = Repository('repo1')	
		repo2 = Repository('repo2')	
		repo1.add_task('task1', ["echo task1"])	
		repo1.add_task('task2', [{CMD:"echo something echoed", INFO:id}, "./lalala gh"])
		repo2.add_task('task1', [])
		repo2.add_task('task2', ["ls"])	
		TestFarmClient('a client', [repo1, repo2],[listener])
		self.assertEquals("""\

('BEGIN_REPOSITORY', 'repo1', '2006-03-17-13-26-20'),
('BEGIN_TASK', 'task1'),
('CMD', 'echo task1', True, '', '', {}),
('END_TASK', 'task1'),
('BEGIN_TASK', 'task2'),
('CMD', 'echo something echoed', True, '', 'something echoed', {}),
('CMD', './lalala gh', False, 'sh: ./lalala: No such file or directory', '', {}),
('END_TASK', 'task2'),
('END_REPOSITORY', 'repo1', '2006-03-17-13-26-20', False),

('BEGIN_REPOSITORY', 'repo2', '2006-03-17-13-26-20'),
('BEGIN_TASK', 'task1'),
('END_TASK', 'task1'),
('BEGIN_TASK', 'task2'),
('CMD', 'ls', True, '', '', {}),
('END_TASK', 'task2'),
('END_REPOSITORY', 'repo2', '2006-03-17-13-26-20', True),
""", open( listener.logfile ).read() )
	
	def xtest_idle_state(self):
		repo.check_for_new_commits( check_cmd="cvs -nq up -dP | grep ^[UP]", minutes_idle=5 )
		listener = ServerListener()
			
		

