
from server import Server
import deansi
import datetime

detailsTemplate = """\
<!DOCTYPE HTML>
<html lang="en-US">
<head>
<meta charset="utf-8">
<title>TestFarm: Execution details for {project} :: {client} :: {execution}</title>
<style>
{deansi_style}
</style>
<link href="style.css" rel="stylesheet" type="text/css">
<script type="text/javascript" language="JavaScript" src="testfarm.js"></script>
</head>
<body>

{content}
<div class="about">
<p>TestFarm is free software.
Learn <a href="http://testfarm.sf.net/">about TestFarm</a>.</p>
</div>
</body>
</html>
"""

class ExecutionDetails(object) :
	def contentBlock(self, kind, content, id) :
		id = kind+id
		return (
			'	<div id="{id}" class="{kind}">\n'
			'		<div class="{kind}_header">{KIND}:</div>\n'
			'		<div class="plain_text">{content}</div>\n'
			'	</div>\n'
			'{expander}'
			.format(
				id = id,
				kind = kind,
				KIND = kind.upper(),
				content = deansi.deansi(content),
				expander = "" if content.count("\n") <= 10 else
					"	<script type='text/javascript'>"
						"togglesize('{}');</script>\n".format(id),
				)
			)
	def command(self, command) :
		status = (
			"RUNNING" if command.running else
			"OK" if command.ok else "FAILED")
		indicatorclass = "command_"+(
			"running" if command.running else
			"ok" if command.ok else "failure")

		id  = "1_1" # TODO: Compute it!!!!

		return (
			"<div class='command'>\n"
			"	Command: <span class='command_line'>'{commandline}'</span>\n"
			'	<span class="{indicatorclass}">[{indicatortext}]</span>\n'
			'{outputblock}'
			'{infoblock}'
			'{statsblock}'
			'</div>\n'
			.format(
				commandline = command.commandline,
				indicatorclass = indicatorclass,
				indicatortext = status,
				outputblock = "" if command.running or command.ok else (
					self.contentBlock("output", command.output, id)),
				infoblock = "" if command.running or command.info is None else (
					self.contentBlock("info", command.info, id)),
				statsblock = "" if command.running or not command.stats else (
					'	<div class="stats">\n'
					'		<div class="stats_header">Statistics:</div>\n'+
					"".join([
						"		<b>{}:</b> {}<br />\n".format(param, value)
						for param, value in sorted(command.stats.iteritems()) ]) +
					'	</div>\n'
					),
				)
			)

	def task(self, task) :
		commandBlock = "" if not task.commands else "".join([
			self.command(command)
			for command in task.commands])
		return (
			'<div class="task">\n'
			'Task: "{description}"\n'
			'{commandblock}'
			'</div>\n\n'
			).format(
				description = task.description,
				commandblock = commandBlock,
			)

	def execution(self, execution) :
		taskBlock = "" if not execution.tasks else "".join([
			self.task(task)
			for task in execution.tasks])
		endblock = (
			"<p>Execution '{id}' still running...</p>\n".format(
				id=execution.starttime,
				)
			if execution.running else
			"<p>Execution '{id}' finalized with a <b>{status}</b></p>\n".format(
				id=execution.starttime,
				status = "SUCCESS" if execution else "FAILURE"
				)
			)
			
		return (
			"<h1>Details for execution '{id}'</h1>\n"
			"<div class='execution'>\n"
			"<p>Started at {starttime:%Y-%m-%d %H:%M:%S}</p>\n"
			"{taskblock}"
			"{endblock}"
			'</div>\n'
			).format(
				id = execution.starttime,
				starttime = datetime.datetime.strptime(
					execution.starttime, "%Y%m%d-%H%M%S"),
				taskblock = taskBlock,
				endblock = endblock,
			)

	def generate(self, server, project, client, execution) :
		executionSummary = server.execution(project, client, execution)
		executionInfo = server.executionInfo(project, client, execution)
		return detailsTemplate.format(
			project = project,
			client = client,
			execution = execution,
			deansi_style = deansi.styleSheet(),
			content = ExecutionDetails().execution(executionSummary),
			)


class JsonSummary(object) :

	def client(self, server, project, client, now=datetime.datetime.now()) :
		meta = server.clientMetadata(project,client)
		executions = server.executions(project, client)
		expectedIdle = server.expectedIdle(project, client)
		status = "int"
		doing = "wait" if expectedIdle>now and executions else "old"
		currentTask = None
		failedTasks = []
		lastExecution = datetime.datetime(1900,1,1,0,0,0)

		for executionName in reversed(executions) :
			execution = server.execution(project, client, executionName)
			if execution.running :
				if currentTask : continue
				currentTask = execution.currentTask[1]
				doing = "run"
				continue
			# last finished execution
			failedTasks = execution.failedTasks
			status = 'red' if execution.failedTasks else "green"
			lastExecution = datetime.datetime.strptime(
				executionName,"%Y%m%d-%H%M%S")
			break

		failedTasksBlock = '' if not failedTasks else (
			'			"failedTasks" : [\n' +
			''.join((
			'				"{}",\n'.format(failedTask[1])
			for failedTask in failedTasks
			)) +
			'			],\n'
			)

		currentTaskBlock = '' if not currentTask else (
			'			"currentTask": "{}",\n'.format(currentTask)
			)

		return (
			'		{{\n'
			'			"name": "{client}",\n'
			'			"description": {description},\n'
			'			"name_details": {briefDescription},\n'
			'			"status": "{status}",\n'
			'			"doing": "{doing}",\n'
			'			"lastupdate": "{nextIdle:%Y/%m/%d %H:%M:%S}",\n'
						'{failedTasksBlock}'
			'			"lastExecution": "{lastExecution:%Y/%m/%d %H:%M:%S}",\n'
						'{currentTaskBlock}'
			'		}},\n'
			).format(
				client = client,
				nextIdle = expectedIdle, # TODO: next expected != last received
				description = repr(meta['description']),
				briefDescription = repr(meta['briefDescription']),
				status = status,
				doing = doing,
				lastExecution = lastExecution,
				failedTasksBlock = failedTasksBlock,
				currentTaskBlock = currentTaskBlock,
			)

	def project(self, server, project, now=datetime.datetime.now()) :
		clientsBlock = "".join((
			self.client(server, project, client, now)
			for client in server.clients(project)
			))
		return (
			'{{'
			'	"project" : "{project}",\n'
			'	"lastupdate" : "{now:%Y/%m/%d %H:%M:%S}",\n'
			'	"clients" : [\n'
			'{clientsblock}'
			'	]\n'
			'}}'
		).format(
			now = now,
			project = project,
			clientsblock = clientsBlock,
			)

class ProjectHistory(object) :
	pass






