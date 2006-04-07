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

	def tearDown(self):
		listener = ServerListener( repository_name='repo' )
		listener.clean_log_files()

	def setUp(self):
		listener = ServerListener( repository_name='repo' )
		listener.clean_log_files()

	def test_iterations__one_green_iteration(self):
		listener = ServerListener( repository_name='repo' )
		listener.current_time = lambda : "a date"
		server = TestFarmServer(repository_name='repo')
		repo = Repository('repo')	
		repo.add_task('task1', [])	
		TestFarmClient('a_client', repo, testinglisteners=[listener])
		self.assertEquals(
			{'testing_client' : [('a date', 'a date', 'repo', 'stable')]}, 
			server.iterations() )

	def test_details(self):
		listener = ServerListener( client_name='a_client', repository_name='repo')
		server = TestFarmServer(repository_name='repo')
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
		self.assertEquals( expected, server.single_iteration_details('a_client', '1999-99-99-99-99-99') )

	def test_purged_details(self):
		listener = ServerListener( client_name='a_client', repository_name='repo')
		server = TestFarmServer(repository_name='repo')
		listener.current_time = lambda : "1999-99-99-99-99-99"
		listener.listen_begin_repository("we want this one")
		listener.listen_begin_task("task")
		listener.listen_result("a command", False, "some output", "some info", {'a':1})
		listener.listen_result("a command", False, "some more output", "some more info", {'a':1})
		listener.listen_end_task("task")
		listener.current_time = lambda : "2000-00-00-00-00-00"
		listener.listen_end_repository("we want this one", False)
		expected = [
('BEGIN_REPOSITORY', 'we want this one', '1999-99-99-99-99-99'),
('BEGIN_TASK', 'task'),
('CMD', 'a command', False, 'some output', 'some info', {'a':1}),
('END_TASK', 'task'),
('END_REPOSITORY', 'we want this one', '2000-00-00-00-00-00', False),
]
		server.purge_client_logfile('a_client')
		self.assertEquals( expected, server.single_iteration_details('a_client', '1999-99-99-99-99-99') )

	def test_two_clients(self):
		listener1 = ServerListener(
			client_name='client 1', 
			logs_base_dir='/tmp/clients_testdir', 
			repository_name='repo')
		listener2 = ServerListener(
			client_name='client 2', 
			logs_base_dir='/tmp/clients_testdir', 
			repository_name='repo')
		listener1.current_time = lambda : "some date"
		listener2.current_time = lambda : "some other date"
		server = TestFarmServer(logs_base_dir='/tmp/clients_testdir', repository_name='repo')
		repo = Repository('repo')
		repo.add_task('task1', [])

		TestFarmClient('a_client', repo, testinglisteners=[listener1])
		TestFarmClient('another client', repo, testinglisteners=[listener2])
		self.assertEquals( 
			{'client 1':[('some date', 'some date', 'repo', 'stable')],
			 'client 2':[('some other date', 'some other date', 'repo', 'stable')]}, 
			server.iterations() )
		listener1.clean_log_files()
		listener2.clean_log_files()

	def test_idles(self):
		listener = ServerListener(repository_name='repo', client_name='a_client')
		listener.current_time = lambda : "a date"
		server = TestFarmServer(repository_name='repo')
		repo = Repository('repo')	
		repo.add_checking_for_new_commits( checking_cmd="echo P patched_file | grep ^[UP]", minutes_idle=1 )
		TestFarmClient('a_client', repo, testinglisteners=[listener])
		self.assertEquals(
			{'a_client' : 
				{'date':'a date', 
				'new_commits_found': True,
				'next_run_in_seconds':60
				}
			}, 
			server.idle() )

	def test_stats_single_client_single_key(self):
		listener = ServerListener(repository_name='repo', client_name='a_client')
		server = TestFarmServer(repository_name='repo')

		listener.current_time = lambda : "2006-04-04-00-00-00"
		repo = Repository('repo')	
		repo.add_task("task", [{STATS:lambda x: {'key':5} }] )
		TestFarmClient('a_client', repo, testinglisteners=[listener])
		
		listener.current_time = lambda : "2006-04-05-00-00-00"
		repo = Repository('repo')	
		repo.add_task("task", [{STATS:lambda x: {'key':1} }] )
		TestFarmClient('a_client', repo, testinglisteners=[listener])
		
		self.assertEquals(
			{
			'a_client': 
				{
				'task': [
					('2006-04-04-00-00-00', {'key': 5}), 
					('2006-04-05-00-00-00', {'key': 1})
					]
				}
			}, server.collect_stats() )

	def test_no_stats(self):
		listener = ServerListener(repository_name='repo', client_name='a_client')
		server = TestFarmServer(repository_name='repo')

		listener.current_time = lambda : "2006-04-04-00-00-00"
		repo = Repository('repo')	
		repo.add_task("task", ["echo no stats"] )
		TestFarmClient('a_client', repo, testinglisteners=[listener])
		
		self.assertEquals( {'a_client': {} }, server.collect_stats() )

	def test_stats_single_client_multiple_key(self):
		listener = ServerListener(repository_name='repo', client_name='a_client')
		server = TestFarmServer(repository_name='repo')

		listener.current_time = lambda : "2006-04-04-00-00-00"
		repo = Repository('repo')	
		repo.add_task("task", [{STATS:lambda x: {'key1':5, 'key2':0} }] )
		TestFarmClient('a_client', repo, testinglisteners=[listener])
		
		listener.current_time = lambda : "2006-04-05-00-00-00"
		repo = Repository('repo')	
		repo.add_task("task", [{STATS:lambda x: {'key1':-1, 'key2':4} }] )
		TestFarmClient('a_client', repo, testinglisteners=[listener])
		
		self.assertEquals( 
			{
			'a_client': 
				{
				'task': 
					[
					('2006-04-04-00-00-00', {'key2': 0, 'key1': 5}),
					('2006-04-05-00-00-00', {'key2': 4, 'key1': -1})
					]
				}
			}, server.collect_stats() )


	def test_stats_multiple_client_single_key(self):
		listener1 = ServerListener(repository_name='repo', client_name='client1')
		listener2 = ServerListener(repository_name='repo', client_name='client2')
		server = TestFarmServer(repository_name='repo')

		listener1.current_time = lambda : "2006-04-04-00-00-00"
		repo = Repository('repo')	
		repo.add_task("task", [{STATS:lambda x: {'key':5} }] )
		TestFarmClient('client1', repo, testinglisteners=[listener1])
		
		listener1.current_time = lambda : "2006-04-05-00-00-00"
		repo = Repository('repo')	
		repo.add_task("task", [{STATS:lambda x: {'key':1} }] )
		TestFarmClient('client1', repo, testinglisteners=[listener1])
		
		listener2.current_time = lambda : "1000-00-00-00-00-00"
		repo = Repository('repo')	
		repo.add_task("task", [{STATS:lambda x: {'clau':0} }] )
		TestFarmClient('client2', repo, testinglisteners=[listener2])


		self.assertEquals( 
			{
			'client1': 
				{
				'task': 
					[
					('2006-04-04-00-00-00', {'key': 5}),
					('2006-04-05-00-00-00', {'key': 1})
					]
				},
			'client2': 
				{'task': 
					[
					('1000-00-00-00-00-00', {'clau': 0})
					]
				}
			}, server.collect_stats() )

	def test_plot_data_file(self):
		listener1 = ServerListener(repository_name='repo', client_name='client1')
		listener2 = ServerListener(repository_name='repo', client_name='client2')
		server = TestFarmServer(repository_name='repo')

		listener1.current_time = lambda : "2006-04-04-00-00-00"
		repo = Repository('repo')	
		repo.add_task("task", [{STATS:lambda x: {'key':5} }] )
		TestFarmClient('client1', repo, testinglisteners=[listener1])
		
		listener1.current_time = lambda : "2006-04-05-00-00-00"
		repo = Repository('repo')	
		repo.add_task("task", [{STATS:lambda x: {'kk':3} }, {STATS:lambda x: {'key':1, 'key2':2} }] )
		TestFarmClient('client1', repo, testinglisteners=[listener1])
		
		listener2.current_time = lambda : "2000-01-01-12-54-00"
		repo = Repository('repo')	
		repo.add_task("task", [{STATS:lambda x: {'clau 1':0, 'clau 2':10} }] )
		repo.add_task("another task", [{STATS:lambda x: {'clau 1':2, 'clau 2':13} }] )
		TestFarmClient('client2', repo, testinglisteners=[listener2])
		
		server.plot_stats()

		self.assertEquals('''\
time	kk	key2	key
2006/04/04.00:00	-	-	5
2006/04/05.00:00	3	-	-
2006/04/05.00:00	-	2	1
''', open("%s/%s/client1_1.plot" % (server.logs_base_dir, server.repository_name)).read() )

		self.assertEquals('''\
time	clau_1	clau_2
2000/01/01.12:54	0	10
''', open("%s/%s/client2_1.plot" % (server.logs_base_dir, server.repository_name)).read() )
		self.assertEquals('''\
time	clau_1	clau_2
2000/01/01.12:54	2	13
''', open("%s/%s/client2_2.plot" % (server.logs_base_dir, server.repository_name)).read() )



	def test_plotdata_no_stats(self):
		listener = ServerListener(repository_name='repo', client_name='a_client')
		server = TestFarmServer(repository_name='repo')

		listener.current_time = lambda : "2006-04-04-00-00-00"
		repo = Repository('repo')	
		repo.add_task("task", ["echo no stats"] )
		TestFarmClient('a_client', repo, testinglisteners=[listener])
		
		server.plot_stats()
#
# Tests ServerListener
#
class Tests_ServerListener(ColoredTestCase):

	def tearDown(self):
		listener = ServerListener( repository_name='repo' )
		listener.clean_log_files()

	def setUp(self):
		listener = ServerListener( repository_name='repo' )
		listener.clean_log_files()

	def test_multiple_repositories_multiple_tasks(self):
		id = lambda txt : txt
		listener1 = ServerListener( repository_name='repo')
		listener2 = ServerListener( repository_name='repo')
		listener1.current_time = lambda : "2006-03-17-13-26-20"
		listener2.current_time = lambda : "2006-03-17-13-26-20"
		repo1 = Repository('repo')	
		repo2 = Repository('repo')	
		repo1.add_task('task1', ["echo task1"])	
		repo1.add_task('task2', [{CMD:"echo something echoed", INFO:id}, "./lalala gh"])
		repo2.add_task('task1', [])
		repo2.add_task('task2', ["ls"])	
		TestFarmClient('a_client', repo1, testinglisteners=[listener1])
		TestFarmClient('a_client', repo2, testinglisteners=[listener2])
		self.assertEquals("""\

('BEGIN_REPOSITORY', 'repo', '2006-03-17-13-26-20'),
('BEGIN_TASK', 'task1'),
('CMD', 'echo task1', True, '', '', {}),
('END_TASK', 'task1'),
('BEGIN_TASK', 'task2'),
('CMD', 'echo something echoed', True, '', 'something echoed\\n', {}),
('CMD', './lalala gh', False, '/bin/sh: ./lalala: No such file or directory\\n', '', {}),
('END_TASK', 'task2'),
('END_REPOSITORY', 'repo', '2006-03-17-13-26-20', False),

('BEGIN_REPOSITORY', 'repo', '2006-03-17-13-26-20'),
('BEGIN_TASK', 'task1'),
('END_TASK', 'task1'),
('BEGIN_TASK', 'task2'),
('CMD', 'ls', True, '', '', {}),
('END_TASK', 'task2'),
('END_REPOSITORY', 'repo', '2006-03-17-13-26-20', True),
""", open( listener2.logfile ).read() )
	
	def test_idle_state(self):
		listener = ServerListener( repository_name='repo' )
		listener.current_time = lambda : "1000-10-10-10-10-10"
		listener.listen_found_new_commits(True, next_run_in_seconds=60)
		self.assertEquals("{'date': '1000-10-10-10-10-10', 'new_commits_found': True, 'next_run_in_seconds': 60}", 
			open(listener.idle_file).read())

			
		

