#!/usr/bin/python

import unittest
from server import Server, ArgPrepender
from server import ProjectNotFound, BadServerPath, ClientNotFound
import os

class ServerTest(unittest.TestCase) :

	def setUp(self) :
		try :
			os.system("rm -rf fixture")
		except Exception, e: 
			print e

	def tearDown(self) :
		os.system("rm -rf fixture")

	def assertFileContent(self, filename, expectedContent) :
		self.assertMultiLineEqual(
			open(filename).read(),
			expectedContent)

	def test_argprepender(self) :

		class Wrapped(object) :
			def callme(self, project, client, execution, param1) :
					return (project, client, execution, param1)

		execution = ArgPrepender(Wrapped(),
			"aproject", "aclient", "anexecution")
		self.assertEqual(
				execution.callme("woo"),
				("aproject", "aclient", "anexecution","woo"))

	def test_assertPathOk(self) :
		s = Server("badpath")
		try :
			s._assertPathOk()
			self.fail("Exception expected")
		except BadServerPath, e:
			self.assertEqual(e.message, "badpath")

	def test_assertProjectOk(self) :
		s = Server("fixture")
		s.createServer()
		try :
			s._assertProjectOk("badproject")
			self.fail("Exception expected")
		except ProjectNotFound, e:
			self.assertEqual(e.message, "Project not found 'badproject'")

	def test_createProject(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s._assertProjectOk("myproject")
		# no exceptiona
		self.assertFileContent("fixture/myproject/metadata",
			"{}")

	def test_assertClientOk(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		try :
			s._assertClientOk("myproject","badclient")
			self.fail("Exception expected")
		except ClientNotFound, e:
			self.assertEqual(e.message, "Client not found 'badclient'")

	def test_assertClientOk_whenAllOk(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject", "myclient")
		s._assertClientOk("myproject","myclient")
		# no exceptiona
		self.assertFileContent("fixture/myproject/myclient/metadata",
			"{}")

	def test_clientStatus_whenStarted(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject", "myclient")
		self.assertEqual(
			s.clientStatus("myproject","myclient"), "NotResponding")

	def test_clientStatus_afterIdle(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject", "myclient")
		s.clientIdle("myproject", "myclient", 30)
		self.assertEqual(
			s.clientStatus("myproject","myclient"), "Idle")

	def test_projectMetadata(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.setProjectMetadata("myproject", 
			key1 = "value1",
			key2 = [4,3,2],
			)
		self.assertEqual(s.projectMetadata("myproject"),
			{'key1': 'value1', 'key2' : [4,3,2]})

	def test_projectMetadata_updates(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.setProjectMetadata("myproject", 
			key1 = "first",
			key2 = [4,3,2],
			)
		s.setProjectMetadata("myproject", 
			key1 = "second",
			key3 = [7,8,9],
			)
		self.assertEqual(s.projectMetadata("myproject"),
			{'key1': 'second', 'key2' : [4,3,2], 'key3' : [7,8,9]})

	def test_clientMetadata(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject","myclient")
		s.setClientMetadata("myproject", "myclient",
			key1 = "value1",
			key2 = [4,3,2],
			)
		self.assertEqual(s.clientMetadata("myproject","myclient"),
			{'key1': 'value1', 'key2' : [4,3,2]})

	def test_clientMetadata_updates(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject","myclient")
		s.setClientMetadata("myproject", "myclient",
			key1 = "first",
			key2 = [4,3,2],
			)
		s.setClientMetadata("myproject", "myclient",
			key1 = "second",
			key3 = [7,8,9],
			)
		self.assertEqual(s.clientMetadata("myproject","myclient"),
			{'key1': 'second', 'key2' : [4,3,2], 'key3' : [7,8,9]})

	def test_projects(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("project1")
		s.createProject("project2")
		self.assertEqual(s.projects(), [
			'project1',
			'project2',
			])

	def test_clients(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("project1")
		s.createClient("project1","client1-1")
		s.createProject("project2")
		s.createClient("project2","client2-1")
		s.createClient("project2","client2-2")
		self.assertEqual(s.clients("project2"), [
			'client2-1',
			'client2-2',
			])

	def setUpExecution(self, server, project, client, execution) :
		s = Server(server)
		s.createServer()
		s.createProject(project)
		s.createClient(project, client)
		e = ArgPrepender(s, project, client, execution)
		return e

	def test_executionStarts_whenBadClient(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		e = ArgPrepender(s, "myproject","badclient","20130301-132313")
		try :
			e.executionStarts(
				timestamp="2013-03-01 13:23:13",
				changelog=[])
			self.fail("Exception expected")
		except ClientNotFound, e:
			self.assertEqual(e.message, "Client not found 'badclient'")

	def test_executionStarts(self) :
		s = self.setUpExecution("fixture", "myproject", "myclient", "20130301-132313")
		s.executionStarts(
			timestamp="2013-03-01 13:23:13",
			changelog=[])

		self.assertEqual(s.executionInfo(),
			dict(
				timestamp="2013-03-01 13:23:13",
				changelog=[],
			))

	def test_executions(self) :
		s = Server('fixture')
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject","myclient")
		s.executionStarts("myproject", "myclient", "20130301-225341",
			timestamp="2013-03-01 22:53:41",
			changelog=[],
			)
		s.executionStarts("myproject", "myclient", "20130302-101313",
			timestamp="2013-03-02 10:13:13",
			changelog=[],
			)

		self.assertEqual(s.executions("myproject","myclient"), [
			'20130301-225341',
			'20130302-101313',
			])

	def test_logRead(self) :
		s = self.setUpExecution("fixture", "myproject", "myclient", "20130301-132313")
		s.executionStarts(
			timestamp="20130301-132313",
			changelog=[])
		s.taskStarts(1, "Task description")
		s.commandStarts(1, 1, "command line options")
		s.commandEnds(1, 1, 
			output="Output\n", 
			ok=True,
			info="Info",
			stats={}
			)
		s.taskEnds(1, True)
		s.executionEnds(True)

		self.assertEqual(s._logRead(),[
			('startExecution',),
			('startTask', 1, 'Task description'),
			('startCommand', 1, 1, 'command line options'),
			('endCommand', 1, 1, 'Output\n', True, 'Info', {}),
			('endTask', 1, True),
			('endExecution', True),
			])


	def test_isRunning_withExecution(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject", "myclient")

		s.executionStarts(
			"myproject", "myclient", "20130301-132313",
			timestamp="2013-03-01 13:23:13",
			changelog=[])

		self.assertEqual(
			s.isRunning("myproject","myclient","20130301-132313"), True)

	def test_isRunning_withEndedExecution(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject", "myclient")

		s.executionStarts(
			"myproject", "myclient", "20130301-132313",
			timestamp="2013-03-01 13:23:13",
			changelog=[])

		s.executionEnds(
			"myproject", "myclient", "20130301-132313", True)

		self.assertEqual(
			s.isRunning("myproject","myclient","20130301-132313"), False)

	def test_isRunning_withClient_noExecutions(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject", "myclient")

		self.assertEqual(
			s.isRunning("myproject","myclient"), False)

	def test_isRunning_client_whenExecutionRunning(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject", "myclient")

		s.executionStarts(
			"myproject", "myclient", "20130301-132313",
			timestamp="2013-03-01 13:23:13",
			changelog=[])

		self.assertEqual(
			s.isRunning("myproject","myclient"), True)

	def test_isRunning_client_whenExecutionEnded(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject", "myclient")

		s.executionStarts(
			"myproject", "myclient", "20130301-132313",
			timestamp="2013-03-01 13:23:13",
			changelog=[])

		s.executionEnds(
			"myproject", "myclient", "20130301-132313", True)

		self.assertEqual(
			s.isRunning("myproject","myclient"), False)

	def test_clientStatus_whenRunning(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject", "myclient")

		s.executionStarts(
			"myproject", "myclient", "20130301-132313",
			timestamp="2013-03-01 13:23:13",
			changelog=[])

		self.assertEqual(
			s.clientStatus("myproject","myclient"), "Running")

	def test_executionSummary_whenStarted(self) :

		s = self.setUpExecution("fixture",
			"myproject","myclient","2013-03-23-20-10-40")

		s.executionStarts()
		execution = s.execution()

		self.assertEqual(execution.starttime, "2013-03-23-20-10-40")
		self.assertEqual(execution.running, True)
		self.assertEqual(execution.tasks, [])
		self.assertTrue("ok" not in execution)

	def test_executionSummary_whenFinished(self) :

		s = self.setUpExecution("fixture",
			"myproject","myclient","2013-03-23-20-10-40")

		s.executionStarts()
		s.executionEnds(True)

		execution = s.execution()

		self.assertEqual(execution.tasks, [])
		self.assertEqual(execution.starttime, "2013-03-23-20-10-40")
		self.assertEqual(execution.running, False)
		self.assertEqual(execution.ok, True)

	def test_executionSummary_taskStarted(self) :

		s = self.setUpExecution("fixture",
			"myproject","myclient","2013-03-23-20-10-40")

		s.executionStarts()
		s.taskStarts(1, "First task")

		execution = s.execution()
		self.assertEqual(1, len(execution.tasks))
		task = execution.tasks[0]

		self.assertEqual(task.id, 1)
		self.assertEqual(task.description, "First task")
		self.assertEqual(task.running, True)
		self.assertEqual(task.commands, [])


	def test_executionSummary_taskEndsOk(self) :

		s = self.setUpExecution("fixture",
			"myproject","myclient","2013-03-23-20-10-40")

		s.executionStarts()
		s.taskStarts(1, "First task")
		s.taskEnds(1, True)

		execution = s.execution()
		self.assertEqual(1, len(execution.tasks))
		task = execution.tasks[0]

		self.assertEqual(task.id, 1)
		self.assertEqual(task.description, "First task")
		self.assertEqual(task.running, False)
		self.assertEqual(task.commands, [])

	def test_currentTask(self) :
		s = self.setUpExecution("fixture",
			"myproject","myclient","2013-03-23-20-10-40")

		s.executionStarts()
		self.assertEqual(s.execution().currentTask, None)

		s.taskStarts(1, "First task")
		self.assertEqual(s.execution().currentTask, (1, "First task"))

		s.taskEnds(1, True)
		self.assertEqual(s.execution().currentTask, (1, "First task"))

		s.taskStarts(2, "Second task")
		self.assertEqual(s.execution().currentTask, (2, "Second task"))

		s.taskEnds(2, False)
		self.assertEqual(s.execution().currentTask, (2, "Second task"))

		s.executionEnds(False)
		self.assertEqual(s.execution().currentTask, None)


	def test_failedTasks(self) :
		s = self.setUpExecution("fixture",
			"myproject","myclient","2013-03-23-20-10-40")

		s.executionStarts()
		self.assertEqual(s.execution().failedTasks, [])

		s.taskStarts(1, "First task")
		self.assertEqual(s.execution().failedTasks, [])

		s.taskEnds(1, True)
		self.assertEqual(s.execution().failedTasks, [])

		s.taskStarts(2, "Second task")
		self.assertEqual(s.execution().failedTasks, [])

		s.taskEnds(2, False)
		self.assertEqual(s.execution().failedTasks, [
			(2, "Second task"),
			])

		s.taskStarts(3, "Third task")
		self.assertEqual(s.execution().failedTasks, [
			(2, "Second task"),
			])

		s.taskEnds(3, False)
		self.assertEqual(s.execution().failedTasks, [
			(2, "Second task"),
			(3, "Third task"),
			])

	def test_executionSummary_commandStats(self) :

		s = self.setUpExecution("fixture",
			"myproject","myclient","2013-03-23-20-10-40")

		s.executionStarts()
		s.taskStarts(1, "First task")
		s.commandStarts(1,1, "acommand param1")
		s.taskEnds(1, True)

		execution = s.execution()
		self.assertEqual(1, len(execution.tasks[0].commands))
		task = execution.tasks[0].commands[0]

		self.assertEqual(task.id, 1)
		self.assertEqual(task.commandline, "acommand param1")
		self.assertEqual(task.running, True)

	def test_executionSummary_commandEndsOk(self) :

		s = self.setUpExecution("fixture",
			"myproject","myclient","2013-03-23-20-10-40")

		s.executionStarts()
		s.taskStarts(1, "First task")
		s.commandStarts(1,1, "acommand param1")
		s.commandEnds(1,1, "output", True, "info", dict(stat1=3,stat2=19))

		execution = s.execution()
		self.assertEqual(1, len(execution.tasks[0].commands))
		command = execution.tasks[0].commands[0]

		self.assertEqual(command.info, "info")
		self.assertEqual(command.output, "output")
		self.assertEqual(command.ok, True)
		self.assertEqual(command.running, False)
		self.assertEqual(command.stats, dict(stat1=3, stat2=19))

	def test_executionSummary_commandEndsFailing(self) :

		s = self.setUpExecution("fixture",
			"myproject","myclient","2013-03-23-20-10-40")

		s.executionStarts()
		s.taskStarts(1, "First task")
		s.commandStarts(1,1, "acommand param1")
		s.commandEnds(1,1, "output", False, "info", dict(stat1=3,stat2=19))

		execution = s.execution()
		self.assertEqual(1, len(execution.tasks[0].commands))
		command = execution.tasks[0].commands[0]

		self.assertEqual(command.info, "info")
		self.assertEqual(command.output, "output")
		self.assertEqual(command.ok, False)
		self.assertEqual(command.running, False)
		self.assertEqual(command.stats, dict(stat1=3, stat2=19))




if __name__ == "__main__" :
	unittest.main()


