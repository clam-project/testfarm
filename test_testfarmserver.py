import unittest
import datetime
from listeners import *
from testfarmclient import *
from testfarmserver import *

class Tests_TestFarmServer(unittest.TestCase):
	pass
	
class Tests_ServerListener(unittest.TestCase):
	def assertEquals(self, expected, result):
		if expected == result :
			return
		red = "\x1b[31;01m"
		green ="\x1b[32;01m"
		yellow = "\x1b[33;01m" # unreadable on white backgrounds
		cyan = "\x1b[36;01m"
		normal = "\x1b[0m"

		index_diff = 0
		for i in range(len(result)):
			if expected[i]!=result[i]:
				index_diff = i
				break
		print "(%s%s%s%s%s)" % (cyan, expected[:index_diff], green, expected[index_diff:], normal)
		print "(%s%s%s%s%s)" % (cyan, result[:index_diff], red, result[index_diff:], normal)
		print "%s vermell %s" % (red, normal)
		
		assert False, "different strings"

	def test_multiple_repositories_multiple_tasks(self):
		listener = ServerListener()
		open(listener.logfile, "w")
		repo1 = Repository('repo1')	
		repo2 = Repository('repo2')	
		repo1.add_task('task1', ["echo task1"])	
		repo1.add_task('task2', ["ls", "./lalala gh"])
		repo2.add_task('task1', [])
		repo2.add_task('task2', ["ls"])	
		TestFarmClient([repo1, repo2],[listener])
		self.assertEquals("""\
BEGIN_REPOSITORY repo1
15-03-2006 19:32:00
BEGIN_TASK task1
('echo task1', 'ok', '', '', {})
END_TASK task1
BEGIN_TASK task2
('ls', 'ok', '', '', {})
('./lalala gh', 'failure', 'sh: ./lalala: No such file or directory', '', {})
END_TASK task2
END_REPOSITORY repo1
15-03-2006 19:32:00

BEGIN_REPOSITORY repo2
15-03-2006 19:32:00
BEGIN_TASK task1
END_TASK task1
BEGIN_TASK task2
('ls', 'ok', '', '', {})
END_TASK task2
END_REPOSITORY repo2
15-03-2006 19:32:00

""", open( listener.logfile ).read() )

