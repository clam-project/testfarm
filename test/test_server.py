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
from coloredtest import ColoredTestCase
from listeners import *
from task import * # TODO : is necessary ? 
from runner import *
from client import Client
from project import Project
from server import Server
from serverlistener import ServerListener

class Tests_Server(ColoredTestCase):

	def tearDown(self):
		a_project = Project('project name')
		listener = ServerListener( project = a_project)
		listener.clean_log_files()

	def setUp(self):
		a_project = Project('project name')
		listener = ServerListener( project = a_project)
		listener.clean_log_files()

	def test_executions__one_green_execution(self):
		a_project = Project('project name')
		listener = ServerListener( project = a_project)
		listener.current_time = lambda : "a date"	
		server = Server(project_name= a_project.name)
		a_client = Client('client name')
		task = Task(a_project, a_client, 'task')
		task.add_subtask('subtask1', [])	
		Runner(task, testinglisteners=[listener])
		self.assertEquals(
			{'testing_client' : [('a date', 'a date', 'task', 'stable')]}, 
			server.get_executions() )

	def test_executions__day_executions__single_client(self):
		a_project = Project('project name')
		listener = ServerListener( project = a_project)
		listener.current_time = lambda : "2006-04-29-12-00-00"
		a_project = Project('project name')
		server = Server(project_name= a_project.name)
		a_client = Client('client name')
		task = Task(a_project, a_client, 'task')
		task.add_subtask('subtask1', [])	
		Runner(task, testinglisteners=[listener])	
		listener.current_time = lambda : "2006-04-30-12-00-00"	
		Runner(task, testinglisteners=[listener])	
		self.assertEquals(
			{'2006-04-30':
				 {'testing_client': [('2006-04-30-12-00-00', '2006-04-30-12-00-00', 'task', 'stable')]},
			'2006-04-29':
				{'testing_client': [('2006-04-29-12-00-00', '2006-04-29-12-00-00', 'task', 'stable')]}
			}, server.day_executions(server.get_executions()) )

	def test_executions__day_executions__multiple_clients__first_client_with_last_day_empty(self):
		a_project = Project('project name')
		a_client = Client('a_client')
		a_client2 = Client('a_client2')
		listener1 = ServerListener( client=a_client, project=a_project )
		listener1.current_time = lambda : "2006-04-29-12-12-00"
		listener2 = ServerListener( client=a_client2, project=a_project )
		listener2.current_time = lambda : "2006-04-29-12-00-00"
		server = Server(project_name= a_project.name)
		task = Task(a_project, a_client, 'task')
		task.add_subtask('subtask1', [])
		Runner(task, testinglisteners=[listener1])
		task = Task(a_project, a_client2, 'task')	
		task.add_subtask('subtask1', [])
		Runner(task, testinglisteners=[listener2])
		listener2.current_time = lambda : "2006-04-30-12-00-00"	
		Runner(task, testinglisteners=[listener2])
		self.assertEquals(
			{'2006-04-30':
				{'a_client2': [('2006-04-30-12-00-00', '2006-04-30-12-00-00', 'task', 'stable')]},
			'2006-04-29':
				{'a_client2': [('2006-04-29-12-00-00', '2006-04-29-12-00-00', 'task', 'stable')],
				'a_client': [('2006-04-29-12-12-00', '2006-04-29-12-12-00', 'task', 'stable')]
				}
			}, server.day_executions(server.get_executions()) )

	def test_executions__day_executions__multiple_clients__last_client_with_first_day_empty(self):
		a_project = Project('project name')
		a_client = Client('a_client')
		a_client2 = Client('a_client2')
		listener1 = ServerListener( client=a_client, project=a_project )
		listener1.current_time = lambda : "2006-04-29-12-12-00"
		server = Server(project_name= a_project.name)
		task = Task(a_project, a_client, 'task')	
		task.add_subtask('subtask1', [])	
		Runner(task, testinglisteners=[listener1])
		listener1.current_time = lambda : "2006-04-30-12-12-00"
		listener2 = ServerListener( client=a_client2, project=a_project )
		listener2.current_time = lambda : "2006-04-30-12-00-00"	
		Runner(task, testinglisteners=[listener1])
		task = Task(a_project, a_client2, 'task')	
		task.add_subtask('subtask1', [])		
		Runner(task, testinglisteners=[listener2])
		self.assertEquals(
			{'2006-04-30':
				{'a_client2': [('2006-04-30-12-00-00', '2006-04-30-12-00-00', 'task', 'stable')],
				'a_client': [('2006-04-30-12-12-00', '2006-04-30-12-12-00', 'task', 'stable')]
				},
			'2006-04-29':
				{'a_client': [('2006-04-29-12-12-00', '2006-04-29-12-12-00', 'task', 'stable')]}
			}, server.day_executions(server.get_executions()) )


	def test_details(self):
		a_project = Project('project name')
		a_client = Client('a_client')
		listener = ServerListener( client=a_client, project=a_project )
		server = Server(project_name= a_project.name)
		listener.current_time = lambda : "2004-03-17-13-26-20"
		listener.listen_begin_task("not wanted")
		listener.listen_begin_subtask("subtask")
		listener.listen_end_subtask("subtask")
		listener.listen_end_task("name", False)
		listener.current_time = lambda : "1999-99-99-99-99-99"
		listener.listen_begin_task("we want this one")
		listener.listen_begin_subtask("subtask")
		listener.listen_begin_command("a command")
		listener.listen_end_command("a command", False, "", "some info", {'a':1})
		listener.listen_end_subtask("subtask")
		listener.current_time = lambda : "2000-00-00-00-00-00"
		listener.listen_end_task("we want this one", False)
		listener.current_time = lambda : "2005-03-17-13-26-20"
		listener.listen_begin_task("not wanted either")
		listener.listen_begin_subtask("subtask")
		listener.listen_end_subtask("subtask")
		listener.listen_end_task("name", False)
		expected = [
('BEGIN_TASK', 'we want this one', '1999-99-99-99-99-99'),
('BEGIN_SUBTASK', 'subtask'),
('BEGIN_CMD', 'a command'),
('END_CMD', 'a command', False, '', 'some info', {'a':1}),
('END_SUBTASK', 'subtask'),
('END_TASK', 'we want this one', '2000-00-00-00-00-00', 'False'),
]
		self.assertEquals( expected, server.single_execution_details('a_client', '1999-99-99-99-99-99') )

	def test_purged_details(self):
		a_project = Project('project name')
		a_client = Client('a_client')
		listener = ServerListener( client=a_client, project=a_project )
		server = Server(project_name= a_project.name)
		listener.current_time = lambda : "1999-99-99-99-99-99"
		listener.listen_begin_task("we want this one")
		listener.listen_begin_subtask("subtask")
		listener.listen_begin_command("a command")
		listener.listen_end_command("a command", False, "some output", "some info", {'a':1})
		listener.listen_begin_command("a command")
		listener.listen_end_command("a command", False, "some more output", "some more info", {'a':1})
		listener.listen_end_subtask("subtask")
		listener.current_time = lambda : "2000-00-00-00-00-00"
		listener.listen_end_task("we want this one", False)
		expected = [
('BEGIN_TASK', 'we want this one', '1999-99-99-99-99-99'),
('BEGIN_SUBTASK', 'subtask'),
('BEGIN_CMD', 'a command'),
('END_CMD', 'a command', False, 'some output', 'some info', {'a':1}),
('BEGIN_CMD', 'a command'),
('END_CMD', 'a command', False, 'some more output','some more info', {'a':1}),
('END_SUBTASK', 'subtask'),
('END_TASK', 'we want this one', '2000-00-00-00-00-00', 'False'),
]
		server.purge_client_logfile('a_client','1999-99-99-99-99-99')
		self.assertEquals( expected, server.single_execution_details('a_client', '1999-99-99-99-99-99') )		

	def test_two_clients(self):
		a_project = Project('project name')
		a_client = Client('client 1')
		a_client2 = Client('client 2')
		listener1 = ServerListener(
			client=a_client, 
			logs_base_dir='/tmp/clients_testdir', 
			project=a_project)
		listener2 = ServerListener(
			client=a_client2, 
			logs_base_dir='/tmp/clients_testdir', 
			project=a_project)
		listener1.current_time = lambda : "some date"
		listener2.current_time = lambda : "some other date"
		server = Server(logs_base_dir='/tmp/clients_testdir', project_name= a_project.name)	
		task = Task(a_project, a_client, 'task')	
		task.add_subtask('subtask1', [])

		Runner(task, testinglisteners=[listener1])
		task = Task(a_project, a_client2, 'task')
		task.add_subtask('subtask1', [])
		Runner(task, testinglisteners=[listener2])
		self.assertEquals( 
			{'client 1':[('some date', 'some date', 'task', 'stable')],
			 'client 2':[('some other date', 'some other date', 'task', 'stable')]}, 
			server.get_executions() )
		listener1.clean_log_files()
		listener2.clean_log_files()

	def test_idles(self):
		a_project = Project('project name')
		a_client = Client('a_client')
		listener = ServerListener( client=a_client, project=a_project )
		listener.current_time = lambda : "a date"
		server = Server(project_name= a_project.name)
		task = Task(a_project, a_client, 'task')
		task.set_check_for_new_commits( checking_cmd="echo P patched_file | grep ^[UP]", minutes_idle=1 )
		Runner(task, testinglisteners=[listener])
		self.assertEquals(
			{'a_client' : 
				{'date':'a date', 
				'new_commits_found': True,
				'next_run_in_seconds':60
				}
			}, 
			server.idle() )

	def test_stats_single_client_single_key(self):
		a_project = Project('project name')
		a_client = Client('a_client')
		listener = ServerListener( client=a_client, project=a_project )
		server = Server(project_name= a_project.name)

		listener.current_time = lambda : "2006-04-04-00-00-00"
		task = Task(a_project, a_client, 'task')
		task.add_subtask("subtask", [{STATS:lambda x: {'key':5} }] )
		Runner(task, testinglisteners=[listener])
		
		listener.current_time = lambda : "2006-04-05-00-00-00"
		task = Task(a_project, a_client, 'task')
		task.add_subtask("subtask", [{STATS:lambda x: {'key':1} }] )
		Runner(task, testinglisteners=[listener])
		
		self.assertEquals(
			{
			'a_client': 
				{
				'subtask': [
					('2006-04-04-00-00-00', {'key': 5}), 
					('2006-04-05-00-00-00', {'key': 1})
					]
				}
			}, server.collect_stats() )

	def test_no_stats(self):
		a_project = Project('project name')
		a_client = Client('a_client')
		listener = ServerListener( client=a_client, project=a_project )
		server = Server(project_name= a_project.name)

		listener.current_time = lambda : "2006-04-04-00-00-00"
		task = Task(a_project, a_client, 'task')
		task.add_subtask("subtask", ["echo no stats"] )
		Runner(task, testinglisteners=[listener])
		
		self.assertEquals( {'a_client': {} }, server.collect_stats() )

	def test_stats_single_client_multiple_key(self):
		a_project = Project('project name')
		a_client = Client('a_client')
		listener = ServerListener( client=a_client, project=a_project )
		server = Server(project_name= a_project.name)

		listener.current_time = lambda : "2006-04-04-00-00-00"
		task = Task(a_project, a_client, 'task')	
		task.add_subtask("subtask", [{STATS:lambda x: {'key1':5, 'key2':0} }] )
		Runner(task, testinglisteners=[listener])
		
		listener.current_time = lambda : "2006-04-05-00-00-00"
		task = Task(a_project, a_client, 'task')		
		task.add_subtask("subtask", [{STATS:lambda x: {'key1':-1, 'key2':4} }] )
		Runner(task, testinglisteners=[listener])
		
		self.assertEquals( 
			{
			'a_client': 
				{
				'subtask': 
					[
					('2006-04-04-00-00-00', {'key2': 0, 'key1': 5}),
					('2006-04-05-00-00-00', {'key2': 4, 'key1': -1})
					]
				}
			}, server.collect_stats() )


	def test_stats_multiple_client_single_key(self):
		a_project = Project('project name')
		a_client = Client('client1')
		a_client2 = Client('client2')
		listener1 = ServerListener( client=a_client, project=a_project )
		listener2 = ServerListener( client=a_client2, project=a_project )
		server = Server(project_name= a_project.name)

		listener1.current_time = lambda : "2006-04-04-00-00-00"
		task = Task(a_project, a_client, 'task')	
		task.add_subtask("subtask", [{STATS:lambda x: {'key':5} }] )
		Runner(task, testinglisteners=[listener1])
		
		listener1.current_time = lambda : "2006-04-05-00-00-00"
		task = Task(a_project, a_client, 'task')	
		task.add_subtask("subtask", [{STATS:lambda x: {'key':1} }] )
		Runner(task, testinglisteners=[listener1])
		
		listener2.current_time = lambda : "1000-00-00-00-00-00"
		task = Task(a_project, a_client, 'task')	
		task.add_subtask("subtask", [{STATS:lambda x: {'clau':0} }] )
		Runner(task, testinglisteners=[listener2])


		self.assertEquals( 
			{
			'client1': 
				{
				'subtask': 
					[
					('2006-04-04-00-00-00', {'key': 5}),
					('2006-04-05-00-00-00', {'key': 1})
					]
				},
			'client2': 
				{'subtask': 
					[
					('1000-00-00-00-00-00', {'clau': 0})
					]
				}
			}, server.collect_stats() )

	def test_plot_data_file(self):
		a_project = Project('project name')
		a_client = Client('client1')
		a_client2 = Client('client2')
		listener1 = ServerListener( client=a_client, project=a_project )
		listener2 = ServerListener( client=a_client2, project=a_project )
		server = Server(project_name= a_project.name)

		listener1.current_time = lambda : "2006-04-04-00-00-00"
		task = Task(a_project, a_client, 'task')	
		task.add_subtask("subtask", [{STATS:lambda x: {'key':5} }] )
		Runner(task, testinglisteners=[listener1])
		
		listener1.current_time = lambda : "2006-04-05-00-00-00"
		task = Task(a_project, a_client, 'task')	
		task.add_subtask("subtask", [{STATS:lambda x: {'kk':3} }, {STATS:lambda x: {'key':1, 'key2':2} }] )
		Runner(task, testinglisteners=[listener1])
		
		listener2.current_time = lambda : "2000-01-01-12-54-00"
		task = Task(a_project, a_client, 'task')	
		task.add_subtask("subtask", [{STATS:lambda x: {'clau 1':0, 'clau 2':10} }] )
		task.add_subtask("another subtask", [{STATS:lambda x: {'clau 1':2, 'clau 2':13} }] )
		Runner(task, testinglisteners=[listener2])
		
		server.plot_stats()

		self.assertEquals('''\
time	kk	key2	key
2006/04/04.00:00	-	-	5
2006/04/05.00:00	3	-	-
2006/04/05.00:00	-	2	1
''', open("%s/%s/client1_1.plot" % (server.logs_base_dir, server.project_name)).read() )

		self.assertEquals('''\
time	clau_1	clau_2
2000/01/01.12:54	0	10
''', open("%s/%s/client2_1.plot" % (server.logs_base_dir, server.project_name)).read() )
		self.assertEquals('''\
time	clau_1	clau_2
2000/01/01.12:54	2	13
''', open("%s/%s/client2_2.plot" % (server.logs_base_dir, server.project_name)).read() )


	def test_plotdata_no_stats(self):
		a_project = Project('project name')
		a_client = Client('a_client')
		listener = ServerListener( client=a_client, project=a_project )
		server = Server(project_name= a_project.name)

		listener.current_time = lambda : "2006-04-04-00-00-00"
		a_client = Client('a_client')
		task = Task(a_project, a_client, 'task')		
		task.add_subtask("subtask", ["echo no stats"] )
		Runner(task, testinglisteners=[listener])
		
		server.plot_stats()

	def test_client_info__only_name(self):
		a_project = Project('project name')
		a_client = Client('client name')
		listener = ServerListener( client = a_client, project = a_project)
		server = Server(project_name = a_project.name)
		self.assertEquals(None, server.load_client_info(a_client.name))

	def test_client_info__more_info(self):
		a_project = Project('project name')
		a_client = Client('client name')
		a_client.brief_description = "a brief description"
		a_client.long_description = "a long description"
		a_client.set_attribute('one more attribute', 'one_more_value')
		a_client.set_attribute('another_attribute', 'another value')
		listener = ServerListener( client = a_client, project = a_project)
		server = Server(project_name = a_project.name)
		self.assertEquals( 
[('Brief description', 'a brief description'),
('Long description', 'a long description'),
('another_attribute', 'another value'),
('one more attribute', 'one_more_value')]
, server.load_client_info(a_client.name))

	def test_project_info__only_name(self):
		a_project = Project('project name')
		a_client = Client('client name')
		listener = ServerListener( client = a_client, project = a_project)
		server = Server(project_name = a_project.name)
		self.assertEquals(None, server.load_project_info())
	
	def test_project_info__more_info(self):
		a_project = Project('project name')
		a_client = Client('client name')
		a_project.brief_description = "a brief description"
		a_project.set_attribute('one more attribute', 'one_more_value')
		a_project.set_attribute('another_attribute', 'another value')
		listener = ServerListener( client = a_client, project = a_project)
		server = Server(project_name = a_project.name)
		self.assertEquals(
[('Brief description', 'a brief description'),
('another_attribute', 'another value'),
('one more attribute', 'one_more_value')]
, server.load_project_info())

	def test_send_task_info(self):
		a_project = Project('project name')
		a_client = Client('client name')
		listener = ServerListener( client = a_client, project = a_project)
		server = Server(project_name = a_project.name)
		task = Task(a_project, a_client, 'task')
		task.add_subtask('subtask1', ["echo subtask1"])	
		task.add_subtask('subtask2', [{CMD:"echo something echoed", INFO: lambda x:x}])	
		listener.listen_task_info(task)
		self.assertEquals(
[('BEGIN_TASK', 'task'),
('BEGIN_SUBTASK', 'subtask1'),
('CMD', 'echo subtask1'),
('END_SUBTASK', 'subtask1'),
('BEGIN_SUBTASK', 'subtask2'),
('CMD', 'echo something echoed'),
('END_SUBTASK', 'subtask2'),
('END_TASK', 'task'),]
		, server.load_task_info(a_client.name))#, task.name))




#
# Tests ServerListener
#
class Tests_ServerListener(ColoredTestCase):

	def tearDown(self):
		a_project = Project('project name')
		listener = ServerListener( project = a_project )
		listener.clean_log_files()

	def setUp(self):
		a_project = Project('project name')
		listener = ServerListener( project = a_project )
		listener.clean_log_files()

	def test_multiple_repositories_multiple_tasks(self):
		a_project = Project('project name')
		id = lambda txt : txt
		listener1 = ServerListener( project=a_project)
		listener2 = ServerListener( project=a_project)
		listener1.current_time = lambda : "2006-03-17-13-26-20"
		listener2.current_time = lambda : "2006-03-17-13-26-20"
		a_client = Client('a_client')
		task1 = Task(a_project, a_client, 'task')	
		task2 = Task(a_project, a_client, 'task')	
		task1.add_subtask('subtask1', ["echo subtask1"])	
		task1.add_subtask('subtask2', [{CMD:"echo something echoed", INFO:id}, "./lalala gh"])
		task2.add_subtask('subtask1', [])
		task2.add_subtask('subtask2', ["ls"])	
		Runner(task1, testinglisteners=[listener1])
		Runner(task2, testinglisteners=[listener2])
		self.assertEquals("""\

('BEGIN_TASK', 'task', '2006-03-17-13-26-20'),
('BEGIN_SUBTASK', 'subtask1'),
('BEGIN_CMD', 'echo subtask1'),
('END_CMD', 'echo subtask1', True, '', '', {}),
('END_SUBTASK', 'subtask1'),
('BEGIN_SUBTASK', 'subtask2'),
('BEGIN_CMD', 'echo something echoed'),
('END_CMD', 'echo something echoed', True, '', 'something echoed\\n', {}),
('BEGIN_CMD', './lalala gh'),
('END_CMD', './lalala gh', False, '/bin/sh: ./lalala: not found\\n', '', {}),
('END_SUBTASK', 'subtask2'),
('END_TASK', 'task', '2006-03-17-13-26-20', 'False'),

('BEGIN_TASK', 'task', '2006-03-17-13-26-20'),
('BEGIN_SUBTASK', 'subtask1'),
('END_SUBTASK', 'subtask1'),
('BEGIN_SUBTASK', 'subtask2'),
('BEGIN_CMD', 'ls'),
('END_CMD', 'ls', True, '', '', {}),
('END_SUBTASK', 'subtask2'),
('END_TASK', 'task', '2006-03-17-13-26-20', 'True'),
""", open( listener2.logfile ).read() )
	
	def test_idle_state(self):
		a_project = Project('project name')
		listener = ServerListener( project = a_project )
		listener.current_time = lambda : "1000-10-10-10-10-10"
		listener.listen_found_new_commits(True, next_run_in_seconds=60)
		self.assertEquals("{'date': '1000-10-10-10-10-10', 'new_commits_found': True, 'next_run_in_seconds': 60}", 
			open(listener.idle_file).read())





			
		

