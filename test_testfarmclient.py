import unittest
from listeners import *
from testfarmclient import *

class Tests_TestFarmClient(unittest.TestCase):

	def test_constructor_with_one_task_repository(self):
		repository = Repository("repo name")
		repository.add_task( "taskname" , ["echo hello"] )
		dummylistener = DummyResultListener()
		client = TestFarmClient( 'a client', repository, testinglisteners = [ dummylistener ] )
		self.assertEquals("""\
BEGIN_REPOSITORY repo name
BEGIN_TASK taskname
('echo hello', 'ok', '', '', {})
END_TASK taskname
END_REPOSITORY repo name""", dummylistener.log() )


		


