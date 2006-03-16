import unittest
from listeners import *
from testfarmclient import *

class Tests_TestFarmClient(unittest.TestCase):

	def test_num_repositories_default(self):
		client = TestFarmClient()
		self.assertEquals(0, client.num_repositories() )

	def test_num_repositories_multiple(self):
		repo1, repo2 = Repository(), Repository()
		client = TestFarmClient( [repo1, repo2], listeners = [ NullResultListener() ] )
		self.assertEquals(2, client.num_repositories() )
	
	def test_constructor_with_one_task_repository(self):
		repository = Repository("repo name")
		repository.add_task( "taskname" , ["echo hello"] )
		dummylistener = DummyResultListener()
		client = TestFarmClient( [ repository ], listeners = [ dummylistener ] )
		self.assertEquals("""\
BEGIN_REPOSITORY repo name
BEGIN_TASK taskname
('echo hello', 'ok', '', '', {})
END_TASK taskname
END_REPOSITORY repo name""", dummylistener.log() )


		


