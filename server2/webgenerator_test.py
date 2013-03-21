#!/usr/bin/python

from server import Server, ArgPrepender
from webgenerator import ExecutionDetails, JsonSummary, ProjectHistory
import unittest
import os
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
			'<div id="kind2_32" class="kind">\n'
			'<div class="kind_header">KIND:</div>\n'
			'<div class="plain_text">content</div>\n'
			'</div>\n'
			)

	def test_contantBlock_notSoLongInfo(self) :
		w = ExecutionDetails()
		content = w.contentBlock(
			kind = "kind",
			content="\n".join(str(i+1) for i in xrange(11)),
			id = "2_32",
			)
		self.assertMultiLineEqual(content,
			'<div id="kind2_32" class="kind">\n'
			'<div class="kind_header">KIND:</div>\n'
			'<div class="plain_text">1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11</div>\n'
			'</div>\n'
			)

	def test_contantBlock_longInfo(self) :
		w = ExecutionDetails()
		content = w.contentBlock(
			kind = "kind",
			content="\n".join(str(i+1) for i in xrange(12)),
			id = "2_32",
			)
		self.assertMultiLineEqual( content,
			'<div id="kind2_32" class="kind">\n'
			'<div class="kind_header">KIND:</div>\n'
			'<div class="plain_text">1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12</div>\n'
			'</div>\n'
			"<script type='text/javascript'>togglesize('kind2_32');</script>\n"
			)

	def test_executionDetails_contantBlock_ansiOutput(self) :
		w = ExecutionDetails()
		content = w.contentBlock(
			kind = "kind",
			content="\033[34mBlue\033[0m",
			id = "2_32",
			)

		self.assertMultiLineEqual( content,
			'<div id="kind2_32" class="kind">\n'
			'<div class="kind_header">KIND:</div>\n'
			'<div class="plain_text"><span class=\'ansi_blue\'>Blue</span></div>\n'
			'</div>\n'
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
			"<div class='command' id='command_1_1'>\n"
			"	<span class='command_line'>command line</span>\n"
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
			"<div class='command' id='command_1_1'>\n"
			"	<span class='command_line'>bad command line</span>\n"
			'	<span class="command_failure">[FAILED]</span>\n'
			'<div id="output1_1" class="output">\n'
			'<div class="output_header">OUTPUT:</div>\n'
			'<div class="plain_text">shown output\n</div>\n'
			'</div>\n'
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
			"<div class='command' id='command_1_1'>\n"
			"	<span class='command_line'>command line</span>\n"
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
			"<div class='command' id='command_1_1'>\n"
			"	<span class='command_line'>bad command line</span>\n"
			'	<span class="command_ok">[OK]</span>\n'
			'<div id="info1_1" class="info">\n'
			'<div class="info_header">INFO:</div>\n'
			'<div class="plain_text">information</div>\n'
			'</div>\n'
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
			"<div class='command' id='command_1_1'>\n"
			"	<span class='command_line'>command line</span>\n"
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
			id = 1,
			running = False,
			ok = None,
			info=None,
			stats = {}
			) :
		project, client, execution = "myproject", "myclient", "20130301-232425"
		s = Server("fixture")
		e = ArgPrepender(s, project, client, execution)
		e.executionStarts(
			timestamp="2013-03-01 23:24:25",
			changelog=[])
		e.taskStarts(id, description)
		for i in xrange(commands) :
			output="output for command {}".format(i)
			ok = True
			e.commandStarts(id,i+1, "command line")
			if running : return e.execution().tasks[0]
			e.commandEnds(id,i+1, output=output, ok=ok, info=info, stats=stats)
		e.taskEnds(id,True)
		e.executionEnds(True)
		return e.execution().tasks[id-1]

	def test_task_empty(self) :
		self.setUpEmptyClient()
		task = self.taskFixture("First task", running=False)

		w = ExecutionDetails()
		result = w.task(task)
		self.assertMultiLineEqual(result,
			'<div class="task" id="task_1">\n'
			'TASK: "First task"\n'
			'END OF TASK: "First task"\n'
			'</div>\n\n'
			)

	def test_task_oneCommand(self) :
		self.setUpEmptyClient()
		task = self.taskFixture("First task", running=False, commands=1)

		w = ExecutionDetails()
		result = w.task(task)
		self.assertMultiLineEqual(result,
			'<div class="task" id="task_1">\n'
			'TASK: "First task"\n'
			"<div class='command' id='command_1_1'>\n"
			"	<span class='command_line'>command line</span>\n"
			'	<span class="command_ok">[OK]</span>\n'
			'</div>\n'
			'END OF TASK: "First task"\n'
			'</div>\n\n'
			)

	def setUpEmptyClient(self) :
		s = Server("fixture")

		s.createServer()
		s.createProject("myproject")
		s.createClient("myproject", "myclient")
		s.setClientMetadata("myproject", "myclient",
			description = "a description",
			briefDescription = "brief description",
			)
		# force an idle time
		s.now=datetime.datetime(2013,4,5,6,7,8)
		s.clientIdle("myproject", "myclient", 0)
		return s

	def test_task_twoTasks(self) :
		self.setUpEmptyClient()
		task = self.taskFixture("First task", running=False, commands=1)
		task = self.taskFixture("Second task", id=2, running=False, commands=1)

		w = ExecutionDetails()
		result = w.task(task)
		self.assertMultiLineEqual(result,
			'<div class="task" id="task_2">\n'
			'TASK: "Second task"\n'
			"<div class='command' id='command_2_1'>\n"
			"	<span class='command_line'>command line</span>\n"
			'	<span class="command_ok">[OK]</span>\n'
			'</div>\n'
			'END OF TASK: "Second task"\n'
			'</div>\n\n'
			)


	def executionFixture(self, running = False) :
		project, client, execution = "myproject", "myclient", "20130301-232425"
		s = Server("fixture")
		s.createServer()
		s.createProject(project)
		s.createClient(project, client)
		# force an idle time
		s.now=datetime.datetime(2013,4,5,6,7,8)
		s.clientIdle(project,client, 0)

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
			'<div class="task" id="task_1">\n'
			'TASK: "First task"\n'
			"<div class='command' id='command_1_1'>\n"
			"	<span class='command_line'>command line</span>\n"
			'	<span class="command_ok">[OK]</span>\n'
			'</div>\n'
			'END OF TASK: "First task"\n'
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
			'<div class="task" id="task_1">\n'
			'TASK: "First task"\n'
			"<div class='command' id='command_1_1'>\n"
			"	<span class='command_line'>command line</span>\n"
			'	<span class="command_running">[RUNNING]</span>\n'
			'</div>\n'
			'END OF TASK: "First task"\n'
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
		# force an idle time
		s.now=datetime.datetime(2013,4,5,6,7,8)
		s.clientIdle("myproject", "myclient", 0)

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
		s.now = datetime.datetime(2013,4,5,6,7,8)
		s.createClient("myproject", "myclient")
		s.setClientMetadata("myproject", "myclient",
			description = "a description",
			briefDescription = "brief description",
			)
		# force an idle time
		s.clientIdle("myproject", "myclient", 0)
		s.now = datetime.datetime(2013,4,5,6,7,1)
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
		s.now = datetime.datetime(2013,9,1,2,3,4)

		w = JsonSummary()
		result = w.project(s, 'myproject')
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

		# force an idle time
		s.now=datetime.datetime(2013,4,5,6,7,8)
		s.clientIdle("myproject", "myclient", 0)
		s.clientIdle("myproject", "yourclient", 0)

		s.now = datetime.datetime(2013,9,1,2,3,4)

		w = JsonSummary()
		result = w.project(s, 'myproject')
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


class ProjectHistoryTest(unittest.TestCase) :

	def setUp(self) :
		self.maxDiff = None
		try :
			os.system("rm -rf fixture")
		except Exception as e: 
			print(e)

	def tearDown(self) :
		return
		os.system("rm -rf fixture")

	def setUpProject(self) :
		s = Server("fixture")
		s.createServer()
		s.createProject("myproject")
		return s

	def setUpClient(self, client) :
		s = Server("fixture")
		s.createClient("myproject", client)
		s.setClientMetadata("myproject", client, 
			briefDescription = "brief description",
			)

	def setUpExecution(self, client, name, ok=True, running=False) :
		s = Server("fixture")
		e = ArgPrepender(s, "myproject", client, name)
		timestamp = "{:%Y-%m-%d %H:%M:%S}".format(
			datetime.datetime.strptime(name, "%Y%m%d-%H%M%S"))
		e.executionStarts(
			timestamp= timestamp,
			changelog=[])
		e.taskStarts(1,"First task")
		if running : return
		e.taskEnds(1,ok)
		e.executionEnds(ok)

	def test_execution_green(self) :
		s = self.setUpProject()
		self.setUpClient("myclient")
		self.setUpExecution("myclient", "20130304-050607")
		w = ProjectHistory()
		result = w.execution(s, "myproject", "myclient", "20130304-050607")
		self.assertMultiLineEqual(result,
			'<a href="details-myclient-20130304-050607.html"\n'
			'	title=""Stable. Click to see the details"\n'
			'	class="executionbubble stable">\n'
			"<div>myclient :: brief description</div>\n"
			"<div><b>Started:</b> 2013/03/04 05:06:07</div>\n"
			"<div><b>Finished:</b> 2013/04/05 06:07:08</div>\n"
			'</a>\n'
			)

	def test_execution_red(self) :
		s = self.setUpProject()
		self.setUpClient("myclient")
		self.setUpExecution("myclient", "20130304-050607", ok=False)
		w = ProjectHistory()
		result = w.execution(s, "myproject", "myclient", "20130304-050607")
		self.assertMultiLineEqual(result,
			'<a href="details-myclient-20130304-050607.html"\n'
			'	title=""Broken. Click to see the details"\n'
			'	class="executionbubble broken">\n'
			"<div>myclient :: brief description</div>\n"
			"<div><b>Started:</b> 2013/03/04 05:06:07</div>\n"
			"<div><b>Finished:</b> 2013/04/05 06:07:08</div>\n"
			'</a>\n'
			)
	
	def test_execution_running(self) :
		s = self.setUpProject()
		self.setUpClient("myclient")
		self.setUpExecution("myclient", "20130304-050607", running=True)
		w = ProjectHistory()
		result = w.execution(s, "myproject", "myclient", "20130304-050607")
		self.assertMultiLineEqual(result,
			'<a href="details-myclient-20130304-050607.html"\n'
			'	title=""Running. Click to see the details"\n'
			'	class="executionbubble running">\n'
			"<div>myclient :: brief description</div>\n"
			"<div><b>Started:</b> 2013/03/04 05:06:07</div>\n"
			"<div>in progress...</div>\n"
			'</a>\n'
			)

	# TODO
	def _test_execution_aborted(self) :
		self.assertMultiLineEqual(result,
			'<a href="details-myclient-20130304-050607.html"\n'
			'	title=""Aborted. Click to see the details"\n'
			'	class="executionbubble aborted">\n'
			"<div>myclient :: brief description</div>\n"
			"<div><b>Started:</b> 2013/03/04 05:06:07</div>\n"
			"<div><b>Aborted:</b> 2013/04/05 06:07:08</div>\n"
			'</a>\n'
			)


	def test_executionsByDay(self) :

		w = ProjectHistory()
		clientsExecutions = {
			'myclient1' : [
				'20130101-000000',
				'20130101-200000',
				'20130101-300000',
				'20130102-300000',
				'20130103-300000',
				],
			'myclient2' : [
				'20130101-300000',
				'20130103-100000',
				'20130103-300000',
				'20130104-300000',
				],
			}

		self.assertEqual(
			w.executionsByDay(clientsExecutions),
			[
				('20130104', [
					('myclient1', [
						]),
					('myclient2', [
						'20130104-300000',
						]),
					]),
				('20130103', [
					('myclient1', [
						'20130103-300000',
						]),
					('myclient2', [
						'20130103-300000',
						'20130103-100000',
						]),
					]),
				('20130102', [
					('myclient1', [
						'20130102-300000',
						]),
					('myclient2', [
						]),
					]),
				('20130101', [
					('myclient1', [
						'20130101-300000',
						'20130101-200000',
						'20130101-000000',
						]),
					('myclient2', [
						'20130101-300000',
						]),
					]),
			])

	def test_executionTable(self) :
		s = self.setUpProject()
		self.setUpClient("client 1")
		self.setUpClient("client 2")
		self.setUpExecution("client 1", "20130304-050607", running=True)

		w = ProjectHistory()
		result = w.executionTable(s, "myproject")
		self.assertMultiLineEqual(result,
			'<tr><td colspan="2">2013/03/04</td></tr>\n'
			'<tr>\n'
			'<td>\n'
			'<a href="details-client 1-20130304-050607.html"\n'
			'	title=""Running. Click to see the details"\n'
			'	class="executionbubble running">\n'
			'<div>client 1 :: brief description</div>\n'
			'<div><b>Started:</b> 2013/03/04 05:06:07</div>\n'
			'<div>in progress...</div>\n'
			'</a>\n'
			'</td>\n'
			'<td>\n'
			'</td>\n'
			'</tr>\n'
			)

	def test_executionTable_twoSameClient(self) :
		s = self.setUpProject()
		self.setUpClient("client 1")
		self.setUpClient("client 2")
		self.setUpExecution("client 1", "20130304-050607")
		self.setUpExecution("client 1", "20130304-060708", running=True)

		w = ProjectHistory()
		result = w.executionTable(s, "myproject")
		self.assertMultiLineEqual(result,
			'<tr><td colspan="2">2013/03/04</td></tr>\n'
			'<tr>\n'
			'<td>\n'
			'<a href="details-client 1-20130304-060708.html"\n'
			'	title=""Running. Click to see the details"\n'
			'	class="executionbubble running">\n'
			'<div>client 1 :: brief description</div>\n'
			'<div><b>Started:</b> 2013/03/04 06:07:08</div>\n'
			'<div>in progress...</div>\n'
			'</a>\n'
			'<a href="details-client 1-20130304-050607.html"\n'
			'	title=""Stable. Click to see the details"\n'
			'	class="executionbubble stable">\n'
			'<div>client 1 :: brief description</div>\n'
			'<div><b>Started:</b> 2013/03/04 05:06:07</div>\n'
			'<div><b>Finished:</b> 2013/04/05 06:07:08</div>\n' # invented
			'</a>\n'
			'</td>\n'
			'<td>\n'
			'</td>\n'
			'</tr>\n'
			)

	def test_executionTable_twoSameDay(self) :
		s = self.setUpProject()
		self.setUpClient("client 1")
		self.setUpClient("client 2")
		self.setUpExecution("client 1", "20130304-050607", running=True)
		self.setUpExecution("client 2", "20130304-050607", running=True)

		w = ProjectHistory()
		result = w.executionTable(s, "myproject")
		self.assertMultiLineEqual(result,
			'<tr><td colspan="2">2013/03/04</td></tr>\n'
			'<tr>\n'
			'<td>\n'
			'<a href="details-client 1-20130304-050607.html"\n'
			'	title=""Running. Click to see the details"\n'
			'	class="executionbubble running">\n'
			'<div>client 1 :: brief description</div>\n'
			'<div><b>Started:</b> 2013/03/04 05:06:07</div>\n'
			'<div>in progress...</div>\n'
			'</a>\n'
			'</td>\n'
			'<td>\n'
			'<a href="details-client 2-20130304-050607.html"\n'
			'	title=""Running. Click to see the details"\n'
			'	class="executionbubble running">\n'
			'<div>client 2 :: brief description</div>\n'
			'<div><b>Started:</b> 2013/03/04 05:06:07</div>\n'
			'<div>in progress...</div>\n'
			'</a>\n'
			'</td>\n'
			'</tr>\n'
			)

	def test_executionTable_differentDays(self) :
		s = self.setUpProject()
		self.setUpClient("client 1")
		self.setUpClient("client 2")
		self.setUpExecution("client 1", "20130101-050607", running=True)
		self.setUpExecution("client 2", "20130102-050607", running=True)

		w = ProjectHistory()
		result = w.executionTable(s, "myproject")
		self.assertMultiLineEqual(result,
			'<tr><td colspan="2">2013/01/02</td></tr>\n'
			'<tr>\n'
			'<td>\n'
			'</td>\n'
			'<td>\n'
			'<a href="details-client 2-20130102-050607.html"\n'
			'	title=""Running. Click to see the details"\n'
			'	class="executionbubble running">\n'
			'<div>client 2 :: brief description</div>\n'
			'<div><b>Started:</b> 2013/01/02 05:06:07</div>\n'
			'<div>in progress...</div>\n'
			'</a>\n'
			'</td>\n'
			'</tr>\n'
			'<tr><td colspan="2">2013/01/01</td></tr>\n'
			'<tr>\n'
			'<td>\n'
			'<a href="details-client 1-20130101-050607.html"\n'
			'	title=""Running. Click to see the details"\n'
			'	class="executionbubble running">\n'
			'<div>client 1 :: brief description</div>\n'
			'<div><b>Started:</b> 2013/01/01 05:06:07</div>\n'
			'<div>in progress...</div>\n'
			'</a>\n'
			'</td>\n'
			'<td>\n'
			'</td>\n'
			'</tr>\n'
			)

	def test_clientStatus_green(self) :
		s = self.setUpProject()
		self.setUpClient("myclient")
		self.setUpExecution("myclient", "20130102-050607")
		s.now=datetime.datetime(2013,4,5,6,7,8)
		s.clientIdle("myproject", "myclient", 1)

		w = ProjectHistory()
		data = s.client("myproject", "myclient")
		result = w.clientStatus(data)
		self.assertMultiLineEqual(result,
			'<td>\n'
			'	<div class="client_status stable">Stable</div>\n'
			'	<div class="client_doing wait">Next run:<br />\n'
			'		2013/04/05 06:08:08</div>\n'
			'</td>\n'
			)
		
	def test_clientStatus_red(self) :
		s = self.setUpProject()
		self.setUpClient("myclient")
		self.setUpExecution("myclient", "20130102-050607", ok=False)
		s.now=datetime.datetime(2013,4,5,6,7,8)
		s.clientIdle("myproject", "myclient", 1)

		w = ProjectHistory()
		data = s.client("myproject", "myclient")
		result = w.clientStatus(data)
		self.assertMultiLineEqual(result,
			'<td>\n'
			'	<div class="client_status broken">Broken</div>\n'
			'	<div class="client_doing wait">Next run:<br />\n'
			'		2013/04/05 06:08:08</div>\n'
			'</td>\n'
			)
		
	def test_clientStatus_old(self) :
		s = self.setUpProject()
		self.setUpClient("myclient")
		self.setUpExecution("myclient", "20130102-050607")
		# force an idle time
		s.now=datetime.datetime(2013,4,5,6,7,8)
		s.clientIdle("myproject", "myclient", 1)

		w = ProjectHistory()
		s.now=datetime.datetime(2013,9,5,6,7,8)
		data = s.client("myproject", "myclient")
		result = w.clientStatus(data)
		self.assertMultiLineEqual(result,
			'<td>\n'
			'	<div class="client_status stable">Stable</div>\n'
			'	<div class="client_doing old">Not responding since:<br />\n'
			'		2013/04/05 06:08:08</div>\n'
			'</td>\n'
			)

	def test_clientStatus_running(self) :
		s = self.setUpProject()
		self.setUpClient("myclient")
		self.setUpExecution("myclient", "20130102-050607", running=True)
		# force an idle time
		s.now=datetime.datetime(2013,4,5,6,7,8)
		s.clientIdle("myproject", "myclient", 1)

		w = ProjectHistory()
		s.now=datetime.datetime(2013,9,5,6,7,8)
		data = s.client("myproject", "myclient")
		result = w.clientStatus(data)
		self.assertMultiLineEqual(result,
			'<td>\n'
			'	<div class="client_status unknown">Unknown</div>\n'
			'	<div class="client_doing run">Running since:<br />\n'
			'		2013/01/02 05:06:07</div>\n'
			'</td>\n'
			)






if __name__ == "__main__" :
	unittest.main()


