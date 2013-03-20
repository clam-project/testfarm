#!/usr/bin/python

import unittest
from server import Server, ArgPrepender
from server import ProjectNotFound, BadServerPath, ClientNotFound
import os
from webgenerator import WebGenerator, ExecutionDetails
import deansi

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
		task = self.taskFixture("First task", running=True)

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













class WebGeneratorTest(unittest.TestCase) :


	def _test_executionDetails_emptyExecution(self) :
		s = self.setUpExecution()

		w = WebGenerator("fixture", "output")
		self.assertMultiLineEqual(
			w.executionDetails("myproject","myclient","20130301-232425"),
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

<div class='execution'>
<h1>Details for execution '20130301-232425', started at 2013-03-01 23:24:25</h1>

<p>Execution '20130301-232425' finalized at 2013-03-01 23:34:35</p>
<p>No errors detected</p>
</div>

<div class="about">
<p>TestFarm is free software.
Learn <a href="http://testfarm.sf.net/">about TestFarm</a>.</p>
</div>
</body>
</html>
""")


if __name__ == "__main__" :
	unittest.main()


