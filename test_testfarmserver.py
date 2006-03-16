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
		print "(%s%s%s%s%s)" % (cyan, expectedstr[:index_diff], green, expectedstr[index_diff:], normal)
		print "(%s%s%s%s%s)" % (cyan, resultstr[:index_diff], red, resultstr[index_diff:], normal)
		
		assert False, "different strings"

class Tests_TestFarmServer(ColoredTestCase):
	def test_repository__one_green_iteration(self):
		listener = ServerListener()
		listener.clean_log_files()
		server = TestFarmServer(listener)
		repo = Repository('repo')	
		repo.add_task('task1', [])	
		TestFarmClient([repo],[listener])
		result = server.iterations()
		print server.html_iterations()
		self.assertEquals([('15-03-2006 19:32:00', '15-03-2006 19:32:00', 'stable')], result)
	

class Tests_ServerListener(ColoredTestCase):

	def test_multiple_repositories_multiple_tasks(self):
		id = lambda txt : txt
		listener = ServerListener()
		listener.clean_log_files()
		repo1 = Repository('repo1')	
		repo2 = Repository('repo2')	
		repo1.add_task('task1', ["echo task1"])	
		repo1.add_task('task2', [{CMD:"echo something echoed", INFO:id}, "./lalala gh"])
		repo2.add_task('task1', [])
		repo2.add_task('task2', ["ls"])	
		TestFarmClient([repo1, repo2],[listener])
		self.assertEquals("""\

('BEGIN_REPOSITORY', 'repo1', '15-03-2006 19:32:00'),
('BEGIN_TASK', 'task1'),
('CMD', 'echo task1', True, '', '', {}),
('END_TASK', 'task1'),
('BEGIN_TASK', 'task2'),
('CMD', 'echo something echoed', True, '', 'something echoed', {}),
('CMD', './lalala gh', False, 'sh: ./lalala: No such file or directory', '', {}),
('END_TASK', 'task2'),
('END_REPOSITORY', 'repo1', '15-03-2006 19:32:00', False),

('BEGIN_REPOSITORY', 'repo2', '15-03-2006 19:32:00'),
('BEGIN_TASK', 'task1'),
('END_TASK', 'task1'),
('BEGIN_TASK', 'task2'),
('CMD', 'ls', True, '', '', {}),
('END_TASK', 'task2'),
('END_REPOSITORY', 'repo2', '15-03-2006 19:32:00', True),
""", open( listener.logfile ).read() )

