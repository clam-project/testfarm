
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

		id  = "{}_{}".format(command.task, command.id)
		# TODO: Compute it!!!!

		return (
			"<div class='command' id='command_{id}'>\n"
			"	Command: <span class='command_line'>'{commandline}'</span>\n"
			'	<span class="{indicatorclass}">[{indicatortext}]</span>\n'
			'{outputblock}'
			'{infoblock}'
			'{statsblock}'
			'</div>\n'
			.format(
				id = id,
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
			'<div class="task" id="task_{id}">\n'
			'Task: "{description}"\n'
			'{commandblock}'
			'</div>\n\n'
			).format(
				id = task.id,
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

	def client(self, server, project, client) :
		data = server.client(project, client)
		failedTasksBlock = '' if not data.failedTasks else (
			'			"failedTasks" : [\n' +
			''.join((
				'				"{}",\n'.format(failedTask[1])
				for failedTask in data.failedTasks
			)) +
			'			],\n'
			)
		currentTaskBlock = '' if not data.currentTask else (
			'			"currentTask": "{}",\n'.format(data.currentTask[1])
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
				nextIdle = data.expectedIdle, # TODO: next expected != last received
				description = repr(data.meta.description),
				briefDescription = repr(data.meta.briefDescription),
				status = data.status,
				doing = data.doing,
				lastExecution = data.lastExecution,
				failedTasksBlock = failedTasksBlock,
				currentTaskBlock = currentTaskBlock,
			)

	def project(self, server, project) :
		clientsBlock = "".join((
			self.client(server, project, client)
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
			now = server.now,
			project = project,
			clientsblock = clientsBlock,
			)

class ProjectHistory(object) :

	def execution(self, server, project, client, execution) :
		data = server.execution(project, client, execution)

		# TODO: briefDescription was named task_name in old testfarm
		# TODO: check where to really get it
		meta = server.clientMetadata(project, client)
		try :
			briefDescription = meta["briefDescription"]
		except KeyError :
			briefDescription = "No brief description"

		stoptime = datetime.datetime(2013,4,5,6,7,8)
		starttime = datetime.datetime.strptime(
			data.starttime, "%Y%m%d-%H%M%S")
		status = "running" if data.running else "stable" if data.ok else "broken"
		endBlock = (
			"<div>in progress...</div>\n"
			if data.running else
			"<div><b>Finished:</b> {stoptime:%Y/%m/%d %H:%M:%S}</div>\n"
			.format(
				stoptime = stoptime,
				)
			)
			
		return (
			'<a href="details-{client}-{execution}.html"\n'
			'	title=""{Status}. Click to see the details"\n'
			'	class="execution {status}">\n'
			"<div>{client} :: brief description</div>\n"
			"<div><b>Started:</b> {starttime:%Y/%m/%d %H:%M:%S}</div>\n"
			"{endBlock}"
			'</a>\n'
		).format(
			client = client,
			execution = execution,
			status = status,
			Status = status.capitalize(),
			briefDescription = briefDescription,
			starttime = starttime,
			endBlock = endBlock,
		)

	def executionsByDay(self,clientsExecutions) :
		result = []
		for client in clientsExecutions :
			result += [
				(execution[:8], client, execution)
				for execution in clientsExecutions[client]
				]
		oldDay = None
		final = {}
		for day, client, execution in sorted(result, reverse=True) :
			if day not in final :
				clients = dict(((c,[]) for c in clientsExecutions.keys()))
				final[day] = sorted(clients.items())
			clients[client].append(execution)
		return [a for a in reversed(sorted(final.items()))]


	def executionTable(self, server, project) :
		clientsExecutions = dict( [
			( client, server.executions(project, client))
			for client in server.clients(project) ])

		executionsByDay = self.executionsByDay(clientsExecutions)
		result = [
			'<tr><td colspan="{nclients}" align="center" >'
			'{day:%Y/%m/%d}</td></tr>\n'
			'<tr>\n'
			.format(
				nclients = len(clientsExecutions),
				day = datetime.datetime.strptime(day,"%Y%m%d"),
			) + 
			"".join([
				'<td>\n' +
				"".join([
					self.execution(server, project, client, execution)
					for execution in executions
					]) + 
				'</td>\n'
				for client, executions in clients
				]) +
			'</tr>\n'
			for day, clients in executionsByDay
			]
		return "".join(result)

	def clientStatus(self, server, project, client) :
		data = server.client(project,client)
		statusMap = dict(
			green = "stable",
			red = "broken",
			int = "unknown",
			)
		status = statusMap[data.status]

		if data.doing == "run" :
			doingLine = 'Running since'
			doingTime = data.runningSince
		elif data.doing == 'wait' :
			doingLine = 'Next run'
			doingTime = data.expectedIdle
		else :
			doingLine = 'Not responding since'
			doingTime = data.expectedIdle

		return (
			'<td>\n'
			'	<div class="client_status {status}">{Status}</div>\n'
			'	<div class="client_doing {doing}">{doingPhrase}: '
					'{doingTime:%Y/%m/%d %H:%M:%S}</div>\n'
			'</td>\n'
			).format(
				status = status,
				Status = status.capitalize(),
				doing = data.doing,
				doingPhrase = doingLine,
				doingTime = doingTime,
			)





