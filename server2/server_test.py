#!/usr/bin/python

import unittest
from server import Server, ArgPrepender
from server import ProjectNotFound, BadServerPath, ClientNotFound
import os
import datetime

def emulateExecutionWithStats(self, name, tasks,
		project='myproject', client='myclient') :
	s = Server("fixture")
	s = ArgPrepender(s, project, client, name)
	timestamp = "{:%Y-%m-%d %H:%M:%S}".format(
		datetime.datetime.strptime(name, "%Y%m%d-%H%M%S"))
	s.executionStarts(
		timestamp=timestamp,
		changelog=[])
	for i, (task,commands) in enumerate(tasks) :
		s.taskStarts(i+1,task)
		for j, (line, ok, output, info, stats) in enumerate(commands) :
			s.commandStarts(i+1, j+1, line)
			if ok is None : break # interrupted
			s.commandEnds(i+1, j+1,
				output=output,
				ok=ok,
				info=info,
				stats=stats)
			if ok is False : break # Failed, fatal for the task
		if ok is None : break # interrupted, fatal for the execution
		s.taskEnds(i+1,ok)
	s.executionEnds(ok)


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

		self.assertEqual(command.id, 1)
		self.assertEqual(command.task, 1)
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

		self.assertEqual(command.id, 1)
		self.assertEqual(command.task, 1)
		self.assertEqual(command.info, "info")
		self.assertEqual(command.output, "output")
		self.assertEqual(command.ok, False)
		self.assertEqual(command.running, False)
		self.assertEqual(command.stats, dict(stat1=3, stat2=19))

	def setUpEmptyClient(self, project='myproject', client='myclient', **keyw) :
		s = Server("fixture")
		s.createServer()
		s.createProject(project)
		s.createClient(project,client)
		s.now = datetime.datetime(1900,1,1,0,0,0)
		s.clientIdle(project, client, 0)
		s.setClientMetadata(project,client,**keyw)
		return s

	def emulateExecution(self, name,
			ok = True, running = False,
			project='myproject', client='myclient', **keyw) :
		s = Server("fixture")
		s = ArgPrepender(s, project, client, name)
		timestamp = "{:%Y-%m-%d %H:%M:%S}".format(
			datetime.datetime.strptime(name, "%Y%m%d-%H%M%S"))
		s.executionStarts(
			timestamp=timestamp,
			changelog=[])
		s.taskStarts(1,"First task")
		if running: return
		s.taskEnds(1,ok)
		s.executionEnds(ok)


	def test_clientSummary_noMeta(self) :
		s = self.setUpEmptyClient()
		client = s.client("myproject", "myclient")

		self.assertEqual(client.meta.__dict__, {})

	def test_clientSummary_hasMeta(self) :
		s = self.setUpEmptyClient(
			param1='value1',
			)
		client = s.client("myproject", "myclient")

		self.assertEqual(client.meta.param1, "value1")

	def test_clientSummary_noExecution(self) :
		s = self.setUpEmptyClient()
		s.now = datetime.datetime(2013,3,1,0,0,0)

		client = s.client("myproject", "myclient")

		self.assertEqual(client.name, "myclient")
		self.assertEqual(client.expectedIdle, datetime.datetime(1900,1,1,0,0,0))
		self.assertEqual(client.lastExecution, datetime.datetime(1900,1,1,0,0,0))
		self.assertEqual(client.doing, "old")
		self.assertFalse("ok" in client)
		self.assertEqual(client.failedTasks, [])
		self.assertEqual(client.currentTask, None)

	def test_clientSummary_green(self) :
		s = self.setUpEmptyClient()
		s.now = datetime.datetime(2013,3,1,0,0,0)
		self.emulateExecution("20130301-040506")

		client = s.client("myproject", "myclient")

		self.assertEqual(client.expectedIdle, datetime.datetime(1900,1,1,0,0,0))
		self.assertEqual(client.lastExecution, datetime.datetime(2013,3,1,4,5,6))
		self.assertEqual(client.doing, "old")
		self.assertEqual(client.ok, True)
		self.assertEqual(client.failedTasks, [])
		self.assertEqual(client.currentTask, None)

	def test_clientSummary_red(self) :
		s = self.setUpEmptyClient()
		s.now = datetime.datetime(2013,3,1,0,0,0)
		self.emulateExecution("20130301-040506", ok=False)

		client = s.client("myproject", "myclient")

		self.assertEqual(client.expectedIdle, datetime.datetime(1900,1,1,0,0,0))
		self.assertEqual(client.lastExecution, datetime.datetime(2013,3,1,4,5,6))
		self.assertEqual(client.doing, "old")
		self.assertEqual(client.failedTasks, [(1,"First task")])
		self.assertEqual(client.ok, False)
		self.assertEqual(client.currentTask, None)

	def test_clientSummary_running(self) :
		s = self.setUpEmptyClient()
		s.now = datetime.datetime(2013,3,1,0,0,0)
		self.emulateExecution("20130301-040506", running=True)

		client = s.client("myproject", "myclient")

		self.assertEqual(client.expectedIdle, datetime.datetime(1900,1,1,0,0,0))
		self.assertEqual(client.lastExecution, datetime.datetime(1900,1,1,0,0,0))
		self.assertEqual(client.failedTasks, [])
		self.assertFalse("ok" in client)
		self.assertEqual(client.doing, "run")
		self.assertEqual(client.currentTask, (1,"First task"))

	def test_clientSummary_lastFinishedCounts(self) :
		s = self.setUpEmptyClient()
		s.now = datetime.datetime(2013,3,1,0,0,0)
		self.emulateExecution("20130301-040506")
		self.emulateExecution("20130302-040506", ok=False)

		client = s.client("myproject", "myclient")

		self.assertEqual(client.expectedIdle, datetime.datetime(1900,1,1,0,0,0))
		self.assertEqual(client.lastExecution, datetime.datetime(2013,3,2,4,5,6))
		self.assertEqual(client.doing, "old")
		self.assertEqual(client.failedTasks, [(1,"First task")])
		self.assertEqual(client.ok, False)
		self.assertEqual(client.currentTask, None)


	def test_clientSummary_runningAfterGreen(self) :
		s = self.setUpEmptyClient()
		s.now = datetime.datetime(2013,3,1,0,0,0)
		self.emulateExecution("20130301-040506")
		self.emulateExecution("20130302-040506", running=True)

		client = s.client("myproject", "myclient")

		self.assertEqual(client.expectedIdle, datetime.datetime(1900,1,1,0,0,0))
		self.assertEqual(client.lastExecution, datetime.datetime(2013,3,1,4,5,6))
		self.assertEqual(client.failedTasks, [])
		self.assertEqual(client.ok, True)
		self.assertEqual(client.doing, "run")
		self.assertEqual(client.currentTask, (1,"First task"))

	def test_clientSummary_runningAfterRed(self) :
		s = self.setUpEmptyClient()
		s.now = datetime.datetime(2013,3,1,0,0,0)
		self.emulateExecution("20130301-040506", ok=False)
		self.emulateExecution("20130302-040506", running=True)

		client = s.client("myproject", "myclient")

		self.assertEqual(client.expectedIdle, datetime.datetime(1900,1,1,0,0,0))
		self.assertEqual(client.lastExecution, datetime.datetime(2013,3,1,4,5,6))
		self.assertEqual(client.failedTasks, [(1,"First task")])
		self.assertEqual(client.ok, False)
		self.assertEqual(client.doing, "run")
		self.assertEqual(client.currentTask, (1,"First task"))

	def emulateExecutionWithStats(self, name, tasks,
			project='myproject', client='myclient') :
		s = Server("fixture")
		s = ArgPrepender(s, project, client, name)
		timestamp = "{:%Y-%m-%d %H:%M:%S}".format(
			datetime.datetime.strptime(name, "%Y%m%d-%H%M%S"))
		s.executionStarts(
			timestamp=timestamp,
			changelog=[])
		for i, (task,commands) in enumerate(tasks) :
			s.taskStarts(i+1,task)
			for j, (line, ok, output, info, stats) in enumerate(commands) :
				s.commandStarts(i+1, j+1, line)
				if ok is None : break # interrupted
				s.commandEnds(i+1, j+1,
					output=output,
					ok=ok,
					info=info,
					stats=stats)
				if ok is False : break # Failed, fatal for the task
			if ok is None : break # interrupted, fatal for the execution
			s.taskEnds(i+1,ok)
		s.executionEnds(ok)

	def test_updateStats_noUpdates(self) :
		s = self.setUpEmptyClient()
		self.assertEqual(s.clientStats("myproject", "myclient"), [
		])
		
	def test_updateStats(self) :
		s = self.setUpEmptyClient()
		s.updateStats("myproject","myclient","20130301-040506",dict(
			param1 = 6,
			))
		result = s.clientStats("myproject", "myclient")
		self.assertEqual(result, [
			("20130301-040506", "param1", 6),
		])
		
	def test_updateStats_twoExecutions(self) :
		s = self.setUpEmptyClient()
		s.updateStats("myproject","myclient","20130301-040506",dict(
			param1 = 6,
			))
		s.updateStats("myproject","myclient","20130301-040506",dict(
			param2 = 4,
			))
		result = s.clientStats("myproject", "myclient")
		self.assertEqual(sorted(result), [
			("20130301-040506", "param1", 6),
			("20130301-040506", "param2", 4),
		])
		
	def test_updateStats_twoStats(self) :
		s = self.setUpEmptyClient()
		s.updateStats("myproject","myclient","20130301-040506",dict(
			param1 = 6,
			param2 = 4,
			))
		result = s.clientStats("myproject", "myclient")
		self.assertEqual(sorted(result), [
			("20130301-040506", "param1", 6),
			("20130301-040506", "param2", 4),
		])

	def test_clientStats_singleStat(self) :
		s = self.setUpEmptyClient()
		self.emulateExecutionWithStats("20130301-040506",[
			("FirstTask", [
			("command 1", True, "output1", None, dict(
				param1=4,
				param2=6,
				)),
			]),
			("Second task", [
			("command 2", True, "output2", None, dict(
				param1=1,
				param2=2,
				)),
			]),
			])
		self.emulateExecutionWithStats("20130301-040507",[
			("FirstTask", [
			("command 1", True, "output1", None, dict(
				param1=2,
				param2=3,
				)),
			]),
			])
		result = s.clientStats("myproject", "myclient")
		self.assertEqual(result, [
			("20130301-040506", "param1", 4),
			("20130301-040506", "param2", 6),
			("20130301-040506", "param1", 1),
			("20130301-040506", "param2", 2),
			("20130301-040507", "param1", 2),
			("20130301-040507", "param2", 3),
		])


if __name__ == "__main__" :
	unittest.main()


