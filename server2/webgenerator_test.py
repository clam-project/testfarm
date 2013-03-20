#!/usr/bin/python

import unittest
from server import Server, ArgPrepender
from server import ProjectNotFound, BadServerPath, ClientNotFound
import os
from webgenerator import ExecutionDetails, JsonSummary
import deansi
import datetime

class ExecutionDetailsTest(unittest.TestCase) :

	def setUp(self) :
		self.maxDiff = None
		try :
			os.system("rm -rf fixture")
		except Exception as e: 
			print(e)

	def tearDown(self) :
		return
		os.system("rm -rf fixture")

	def test_contentBlock_withInfo(self) :
		w = ExecutionDetails()
		content = w.contentBlock(
				kind = "kind",
				content="content",
				id = "2_32",
				)
		self.assertMultiLineEqual(content,
			'	<div id="kind2_32" class="kind">\n'
			'		<div class="kind_header">KIND:</div>\n'
			'		<div class="plain_text">content</div>\n'
			'	</div>\n'
			)

	def test_contantBlock_notSoLongInfo(self) :
		w = ExecutionDetails()
		content = w.contentBlock(
			kind = "kind",
			content="\n".join(str(i+1) for i in xrange(11)),
			id = "2_32",
			)
		self.assertMultiLineEqual(content,
			'	<div id="kind2_32" class="kind">\n'
			'		<div class="kind_header">KIND:</div>\n'
			'		<div class="plain_text">1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11</div>\n'
			'	</div>\n'
			)

	def test_contantBlock_longInfo(self) :
		w = ExecutionDetails()
		content = w.contentBlock(
			kind = "kind",
			content="\n".join(str(i+1) for i in xrange(12)),
			id = "2_32",
			)
		self.assertMultiLineEqual( content,
			'	<div id="kind2_32" class="kind">\n'
			'		<div class="kind_header">KIND:</div>\n'
			'		<div class="plain_text">1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12</div>\n'
			'	</div>\n'
			"	<script type='text/javascript'>togglesize('kind2_32');</script>\n"
			)

	def test_executionDetails_contantBlock_ansiOutput(self) :
		w = ExecutionDetails()
		content = w.contentBlock(
			kind = "kind",
			content="\033[34mBlue\033[0m",
			id = "2_32",
			)

		self.assertMultiLineEqual( content,
			'	<div id="kind2_32" class="kind">\n'
			'		<div class="kind_header">KIND:</div>\n'
			'		<div class="plain_text"><span class=\'ansi_blue\'>Blue</span></div>\n'
			'	</div>\n'
			)

	def commandFixture(self, line,
			running = False,
			ok = None,
			output=None,
			info=None,
			stats = {}
			) :
		project, client, execution = "myproject", "myclient", "20130301-232425"
		s = Server("fixture")
		s.createServer()
		s.createProject(project)
		s.createClient(project, client)
		e = ArgPrepender(s, project, client, execution)
		e.executionStarts(
			timestamp="2013-03-01 23:24:25",
			changelog=[])
		e.taskStarts(1, "First task")
		e.commandStarts(1,1, line)
		if running : return e.execution().tasks[0].commands[0]
		e.commandEnds(1,1, output=output, ok=ok, info=info, stats=stats)
		e.taskEnds(1,True)
		e.executionEnds(True)
		return e.execution().tasks[0].commands[0]

	def test_command_ok(self) :
		command = self.commandFixture(
			"command line",
			ok=True,
			output="ignored output",
			)

		w = ExecutionDetails()
		result = w.command(command)
		self.assertMultiLineEqual(result,
			"<div class='command'>\n"
			"	Command: <span class='command_line'>'command line'</span>\n"
			'	<span class="command_ok">[OK]</span>\n'
			'</div>\n'
			)

	def test_command_failed(self) :
		command = self.commandFixture(
			"bad command line",
			ok=False,
			output="shown output\n",
			)

		w = ExecutionDetails()
		result = w.command(command)
		self.assertMultiLineEqual(result,
			"<div class='command'>\n"
			"	Command: <span class='command_line'>'bad command line'</span>\n"
			'	<span class="command_failure">[FAILED]</span>\n'
			'	<div id="output1_1" class="output">\n'
			'		<div class="output_header">OUTPUT:</div>\n'
			'		<div class="plain_text">shown output\n</div>\n'
			'	</div>\n'
			'</div>\n'
			)

	def test_command_running(self) :
		command = self.commandFixture(
			"command line",
			running=True,
			)

		w = ExecutionDetails()
		result = w.command(command)
		self.assertMultiLineEqual(result,
			"<div class='command'>\n"
			"	Command: <span class='command_line'>'command line'</span>\n"
			'	<span class="command_running">[RUNNING]</span>\n'
			'</div>\n'
			)

	def test_command_withInfo(self) :
		command = self.commandFixture(
			"bad command line",
			ok=True,
			info="information",
			)

		w = ExecutionDetails()
		result = w.command(command)
		self.assertMultiLineEqual(result,
			"<div class='command'>\n"
			"	Command: <span class='command_line'>'bad command line'</span>\n"
			'	<span class="command_ok">[OK]</span>\n'
			'	<div id="info1_1" class="info">\n'
			'		<div class="info_header">INFO:</div>\n'
			'		<div class="plain_text">information</div>\n'
			'	</div>\n'
			'</div>\n'
			)

	def test_command_stats(self) :
		command = self.commandFixture(
			"command line",
			ok=True,
			stats=dict(
				param1=300,
				param2=400,
				),
			)

		w = ExecutionDetails()
		result = w.command(command)
		self.assertMultiLineEqual(result,
			"<div class='command'>\n"
			"	Command: <span class='command_line'>'command line'</span>\n"
			'	<span class="command_ok">[OK]</span>\n'
			'	<div class="stats">\n'
			'		<div class="stats_header">Statistics:</div>\n'
			'		<b>param1:</b> 300<br />\n'
			'		<b>param2:</b> 400<br />\n'
			'	</div>\n'
			'</div>\n'
			)

	def taskFixture(self, description,
			commands = 0,
			running = False,
			ok = None,
			info=None,
			stats = {}
			) :
		project, client, execution = "myproject", "myclient", "20130301-232425"
		s = Server("fixture")
		s.createServer()
		s.createProject(project)
		s.createClient(project, client)
		e = ArgPrepender(s, project, client, execution)
		e.executionStarts(
			timestamp="2013-03-01 23:24:25",
			changelog=[])
		e.taskStarts(1, description)
		for i in xrange(commands) :
			output="output for command {}".format(i)
			ok = True
			e.commandStarts(1,i, "command line")
			if running : return e.execution().tasks[0]
			e.commandEnds(1,i, output=output, ok=ok, info=info, stats=stats)
		e.taskEnds(1,True)
		e.executionEnds(True)
		return e.execution().tasks[0]

	def test_task_empty(self) :
		task = self.taskFixture("First task", running=False)

		w = ExecutionDetails()
		result = w.task(task)
		self.assertMultiLineEqual(result,
			'<div class="task">\n'
			'Task: "First task"\n'
			'</div>\n\n'
			)

	def test_task_oneCommand(self) :
		task = self.taskFixture("First task", running=False, commands=1)

		w = ExecutionDetails()
		result = w.task(task)
		self.assertMultiLineEqual(result,
			'<div class="task">\n'
			'Task: "First task"\n'
			"<div class='command'>\n"
			"	Command: <span class='command_line'>'command line'</span>\n"
			'	<span class="command_ok">[OK]</span>\n'
			'</div>\n'
			'</div>\n\n'
			)


	def executionFixture(self, running = False) :
		project, client, execution = "myproject", "myclient", "20130301-232425"
		s = Server("fixture")
		s.createServer()
		s.createProject(project)
		s.createClient(project, client)
		e = ArgPrepender(s, project, client, execution)
		e.executionStarts(
			timestamp="2013-03-01 23:24:25",
			changelog=[])
		e.taskStarts(1, "First task")
		e.commandStarts(1,1, "command line")
		if running : return e.execution()
		e.commandEnds(1,1, output="output", ok=True, info=None, stats={})
		e.taskEnds(1,True)
		e.executionEnds(True)
		return e.execution()

	def test_execution(self) :
		execution = self.executionFixture()

		w = ExecutionDetails()
		result = w.execution(execution)
		self.assertMultiLineEqual(result,
			"<h1>Details for execution '20130301-232425'</h1>\n"
			"<div class='execution'>\n"
			"<p>Started at 2013-03-01 23:24:25</p>\n"
			'<div class="task">\n'
			'Task: "First task"\n'
			"<div class='command'>\n"
			"	Command: <span class='command_line'>'command line'</span>\n"
			'	<span class="command_ok">[OK]</span>\n'
			'</div>\n'
			'</div>\n\n'
			"<p>Execution '20130301-232425' finalized with a <b>SUCCESS</b></p>\n"
			'</div>\n'
			)

	def test_execution_running(self) :
		execution = self.executionFixture(running=True)

		w = ExecutionDetails()
		result = w.execution(execution)
		self.assertMultiLineEqual(result,
			"<h1>Details for execution '20130301-232425'</h1>\n"
			"<div class='execution'>\n"
			"<p>Started at 2013-03-01 23:24:25</p>\n"
			'<div class="task">\n'
			'Task: "First task"\n'
			"<div class='command'>\n"
			"	Command: <span class='command_line'>'command line'</span>\n"
			'	<span class="command_running">[RUNNING]</span>\n'
			'</div>\n'
			'</div>\n\n'
			"<p>Execution '20130301-232425' still running...</p>\n"
			'</div>\n'
			)

	def emptyExecution(self) :
		project, client, execution = "myproject", "myclient", "20130301-232425"
		s = Server("fixture")
		s.createServer()
		s.createProject(project)
		s.createClient(project, client)
		e = ArgPrepender(s, project, client, execution)
		e.executionStarts(
			timestamp="2013-03-01 23:24:25",
			changelog=[])
		e.executionEnds(True)
		return e.execution()

	def test_executionDetails_emptyExecution(self) :
		s = self.emptyExecution()

		w = ExecutionDetails()
		s = Server("fixture")
		content = w.generate(s,"myproject","myclient","20130301-232425")
		self.assertMultiLineEqual( content,
			"""\
<!DOCTYPE HTML>
<html lang="en-US">
<head>
<meta charset="utf-8">
<title>TestFarm: Execution details for myproject :: myclient :: 20130301-232425</title>
<style>
"""+deansi.styleSheet() + """
</style>
<link href="style.css" rel="stylesheet" type="text/css">
<script type="text/javascript" language="JavaScript" src="testfarm.js"></script>
</head>
<body>

<h1>Details for execution '20130301-232425'</h1>
<div class='execution'>
<p>Started at 2013-03-01 23:24:25</p>
<p>Execution '20130301-232425' finalized with a <b>SUCCESS</b></p>
</div>

<div class="about">
<p>TestFarm is free software.
Learn <a href="http://testfarm.sf.net/">about TestFarm</a>.</p>
</div>
</body>
</html>
""")


class JsonSummaryTest(unittest.TestCase) :

	def setUp(self) :
		self.maxDiff = None
		try :
			os.system("rm -rf fixture")
		except Exception as e: 
			print(e)

	def tearDown(self) :
		return
		os.system("rm -rf fixture")


	def setUpEmptyClient(self) :
		s = Server("fixture")

		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject", "myclient")
		s.setClientMetadata("myproject", "myclient",
			description = "a description",
			briefDescription = "brief description",
			)
		return s

	def test_client_noExecutions(self) :

		s = self.setUpEmptyClient()

		w = JsonSummary()
		result = w.client(s, 'myproject', 'myclient')
		self.assertMultiLineEqual(result,
			'		{\n'
			'			"name": "myclient",\n'
			'			"description": \'a description\',\n'
			'			"name_details": \'brief description\',\n'
			'			"status": "int",\n'
			'			"doing": "old",\n'
			'			"lastupdate": "2013/04/05 06:07:08",\n'
			'			"lastExecution": "1900/01/01 00:00:00",\n'
			'		},\n'
			)

	def setUpExecution(self, server, name, running=False, ok=True) :
		e = ArgPrepender(server, "myproject", "myclient", name)
		timestamp = "{:%Y-%m-%d %H:%M:%S}".format(
			datetime.datetime.strptime(name, "%Y%m%d-%H%M%S"))
		e.executionStarts(
			timestamp= timestamp,
			changelog=[])
		e.taskStarts(1, "First task")
		e.commandStarts(1,1, "command line")
		e.commandEnds(1,1, output="output", ok=ok, info=None, stats={})
		if running : return
		e.taskEnds(1,ok)
		e.executionEnds(ok)

		
	def test_client_green(self) :

		s = self.setUpEmptyClient()
		self.setUpExecution(s, "20130506-070809")
		s.clientIdle("myproject", "myclient", 100,
			datetime.datetime(2013,5,6,7,8,9))

		w = JsonSummary()
		result = w.client(s, 'myproject', 'myclient')
		self.assertMultiLineEqual(result,
			'		{\n'
			'			"name": "myclient",\n'
			'			"description": \'a description\',\n'
			'			"name_details": \'brief description\',\n'
			'			"status": "green",\n'
			'			"doing": "wait",\n'
			'			"lastupdate": "2013/04/05 06:07:08",\n'
			'			"lastExecution": "2013/05/06 07:08:09",\n'
			'		},\n'
			)

	def test_client_red(self) :

		s = self.setUpEmptyClient()
		self.setUpExecution(s, "20130506-070809", ok=False)
		s.clientIdle("myproject", "myclient", 100,
			datetime.datetime(2013,5,6,7,8,9))

		w = JsonSummary()
		result = w.client(s, 'myproject', 'myclient')
		self.assertMultiLineEqual(result,
			'		{\n'
			'			"name": "myclient",\n'
			'			"description": \'a description\',\n'
			'			"name_details": \'brief description\',\n'
			'			"status": "red",\n'
			'			"doing": "wait",\n'
			'			"lastupdate": "2013/04/05 06:07:08",\n'
			'			"failedTasks" : [\n'
			'				"First task",\n'
			'			],\n'
			'			"lastExecution": "2013/05/06 07:08:09",\n'
			'		},\n'
			)

	def test_client_greenWhileRunning(self) :
		s = self.setUpEmptyClient()
		self.setUpExecution(s, "20130405-060708")
		self.setUpExecution(s, "20130506-070809", running=True, ok=False)
		w = JsonSummary()
		result = w.client(s, 'myproject', 'myclient')
		self.assertMultiLineEqual(result,
			'		{\n'
			'			"name": "myclient",\n'
			'			"description": \'a description\',\n'
			'			"name_details": \'brief description\',\n'
			'			"status": "green",\n'
			'			"doing": "run",\n'
			'			"lastupdate": "2013/04/05 06:07:08",\n'
			'			"lastExecution": "2013/04/05 06:07:08",\n'
			'			"currentTask": "First task",\n'
			'		},\n'
			)

	def test_client_redWhileRunning(self) :
		s = self.setUpEmptyClient()
		self.setUpExecution(s, "20130405-060708", ok=False)
		self.setUpExecution(s, "20130506-070809", running=True)

		w = JsonSummary()
		result = w.client(s, 'myproject', 'myclient')
		self.assertMultiLineEqual(result,
			'		{\n'
			'			"name": "myclient",\n'
			'			"description": \'a description\',\n'
			'			"name_details": \'brief description\',\n'
			'			"status": "red",\n'
			'			"doing": "run",\n'
			'			"lastupdate": "2013/04/05 06:07:08",\n'
			'			"failedTasks" : [\n'
			'				"First task",\n'
			'			],\n'
			'			"lastExecution": "2013/04/05 06:07:08",\n'
			'			"currentTask": "First task",\n'
			'		},\n'
			)

	def test_project_noClients(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.setProjectMetadata("myproject",
			description = "project description",
			briefDescription = "project brief description",
			)

		w = JsonSummary()
		result = w.project(s, 'myproject', datetime.datetime(2013,9,1,2,3,4))
		self.assertMultiLineEqual(result,
			'{'
			'	"project" : "myproject",\n'
			'	"lastupdate" : "2013/09/01 02:03:04",\n'
			'	"clients" : [\n'
			'	]\n'
			'}'
			)

	def test_project_withClients(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject","myclient")
		s.setClientMetadata("myproject", "myclient",
			description = "a description",
			briefDescription = "brief description",
			)
		s.createClient("myproject","yourclient")
		s.setClientMetadata("myproject", "yourclient",
			description = "your description",
			briefDescription = "your brief description",
			)

		w = JsonSummary()
		result = w.project(s, 'myproject', datetime.datetime(2013,9,1,2,3,4))
		self.assertMultiLineEqual(result,
			'{'
			'	"project" : "myproject",\n'
			'	"lastupdate" : "2013/09/01 02:03:04",\n'
			'	"clients" : [\n'
			'		{\n'
			'			"name": "myclient",\n'
			'			"description": \'a description\',\n'
			'			"name_details": \'brief description\',\n'
			'			"status": "int",\n'
			'			"doing": "old",\n'
			'			"lastupdate": "2013/04/05 06:07:08",\n'
			'			"lastExecution": "1900/01/01 00:00:00",\n'
			'		},\n'
			'		{\n'
			'			"name": "yourclient",\n'
			'			"description": \'your description\',\n'
			'			"name_details": \'your brief description\',\n'
			'			"status": "int",\n'
			'			"doing": "old",\n'
			'			"lastupdate": "2013/04/05 06:07:08",\n'
			'			"lastExecution": "1900/01/01 00:00:00",\n'
			'		},\n'
			'	]\n'
			'}'
			)






if __name__ == "__main__" :
	unittest.main()


