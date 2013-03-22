
from server import Server
import deansi
import datetime

class ExecutionDetails(object) :
	template = """\
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

	def contentBlock(self, kind, content, id) :
		id = kind+id
		return (
			'<div id="{id}" class="{kind}">\n'
			'<div class="{kind}_header">{KIND}:</div>\n'
			'<div class="plain_text">{content}</div>\n'
			'</div>\n'
			'{expander}'
			.format(
				id = id,
				kind = kind,
				KIND = kind.upper(),
				content = deansi.deansi(content),
				expander = "" if content.count("\n") <= 10 else
					"<script type='text/javascript'>"
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
			"	<span class='command_line'>{commandline}</span>\n"
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
			'TASK: "{description}"\n'
			'{commandblock}'
			'END OF TASK: "{description}"\n'
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
		return self.template.format(
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
				description = repr(data.meta.description
					if "description" in data.meta else ""),
				briefDescription = repr(data.meta.briefDescription
					if "briefDescription" in data.meta else ""),
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

	template ="""\
<!DOCTYPE HTML>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="120">
<title>Testfarm History for project {project} </title>
<link href="style.css" rel="stylesheet" type="text/css">
<script language="javascript" type="text/javascript" src="testfarm.js"></script>
<script language="javascript" type="text/javascript" src="jquery.js"></script>
<script language="javascript" type="text/javascript" src="https://www.google.com/jsapi"></script>
<script language="javascript" type="text/javascript" src="plot.js"></script>
</head>

<body>
<div id="theLayer" class="layer"></div>
<h1>testfarm for project <a>{project}
<span class='tooltip'>{description}</span></a>
<span class='description'>{briefDescription}</span>
</h1>
{content}
<div class="about">
<p>TestFarm is free software.
Learn <a href="http://testfarm.sf.net/">about TestFarm</a>.</p>
</div>
</body>
</html>
"""
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
			'	class="executionbubble {status}">\n'
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
			'<tr><td colspan="{nclients}">'
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

	def clientStatus(self,client) :
		statusMap = dict(
			green = "stable",
			red = "broken",
			int = "unknown",
			)
		status = statusMap[client.status]

		if client.doing == "run" :
			doingLine = 'Running since'
			doingTime = client.runningSince
		elif client.doing == 'wait' :
			doingLine = 'Next run'
			doingTime = client.expectedIdle
		else :
			doingLine = 'Not responding since'
			doingTime = client.expectedIdle

		return (
			'<td>\n'
			'	<div class="client_status {status}">{Status}</div>\n'
			'	<div class="client_doing {doing}">{doingPhrase}:<br />\n'
			'		{doingTime:%Y/%m/%d %H:%M:%S}</div>\n'
			'</td>\n'
			).format(
				status = status,
				Status = status.capitalize(),
				doing = client.doing,
				doingPhrase = doingLine,
				doingTime = doingTime,
			)


	# TODO: Untested
	def clientInfo(self, client) :
		return (
			"<th> Client: <a>{name}"
			"<span class='tooltip'>{description}</span></a>"
			"<p width=\"100%%\">{briefDescription}</p></th> "
			).format(
				name = client.name,
				description = client.description
					if "description" in client
					else "",
				briefDescription = client.briefDescription
					if "briefDescription" in client
					else "",
				)


	# TODO: Untested
	def clientStats(self, client) :
		return (
			'<td>'
			'<a href="{client}-stats.html" title="Click to expand">'
			'<div'
				' class="plot thumbnail"'
				' src="{client}-stats.json" /></a>'
			'</td>'
			).format(client = client.name)


	# TODO: Untested
	def generate(self, server, project) :
		clients = [
			server.client(project, client)
			for client in sorted(server.clients(project))
			]
		meta = server.projectMetadata(project)
		return self.template.format(
			project = project,
			description = meta.description if "description" in meta else "",
			briefDescription = meta.briefDescription if 'briefDescription' in meta else "",
			content = (
				'<table class="execution_history">\n'
				'<tr>\n'
				+ ''.join([ self.clientInfo(client) for client in clients ]) +
				'</tr>\n'
				'<tr>\n'
				+ ''.join([ self.clientStatus(client) for client in clients ]) +
				'</tr>\n'
				'<tr>\n'
				+ ''.join([ self.clientStats(client) for client in clients ]) +
				'</tr>'
				+ self.executionTable(server, project) +
				'</table>\n'
				)
		)


# TODO: Untested
class WebGenerator(object) :
	def __init__(self, target) :
		self.target = target
		self.generated = []

	def _p(self, *args) :
		return os.path.join(self.target, *args)

	def copy(self, file, *args) :
		self.write(open(file).read(), *args)

	def write(self, content, *args) :
		filename = self._p(*args)
#		print "Writing",filename
		self.generated.append(filename)
		f = open(filename, 'w')
		f.write(content)
		f.close()

	def generate(self, server) :
		os.mkdir(self._p())
		for project in server.projects() :
			self.generateProject(server, project)

	def generateProject(self, server, project) :
		full = False
		os.mkdir(self._p(project))
		self.copy("style.css", project, "style.css")
		self.copy("testfarm.js", project, "testfarm.js")
		self.copy("plot.js", project, "plot.js")
		self.copy("jquery.js", project, "jquery.js")
		self.copy("summary.html", project, "summary.html")
		writer = ExecutionDetails()
		for client in server.clients(project) :
			for execution in server.executions(project, client) :
				self.write(writer.generate(server,project,client,execution),
					project, "details-"+client+"-"+execution+".html")

			self.write(Stats().generate(server,project, client),
				project, client+"-stats.json")

		writer = ProjectHistory()
		self.write(writer.generate(server, project),
			project, "history.html")
		json = JsonSummary().project(server, project)
		self.write(json,
			project,'testfarm-data.js')
		self.write("callme({})".format(json),
			project, 'testfarm-data.jsond')

		self.write(writer.generate(server, project),
			project, "history.html")

import random

class Stats(object) :
	def generate(self, server, project, client) :
		keys = [ "Tests", "LOC", "Build time" ]
		return (
		'[\n'
		'[ ' + ", ".join([repr(header) for header in (["Execution"] + keys) ]) + ' ],\n'
		+ "".join((
			"[ '{}', ".format(execution) + ", ".join((repr(random.randint(0,400)) for i in keys)) + ' ],\n'
			for execution in server.executions(project, client)
			)) +
		']\n'
		)



if __name__ == "__main__" :

	def setUpExecution(client, name, ok=True, running=False,
			ncommands=1,
			noutputlines=1,
			ntasks=1,
			stats=True,
			) :
		from server import ArgPrepender
		s = Server("fixture")
		e = ArgPrepender(s, "myproject", client, name)
		timestamp = "{:%Y-%m-%d %H:%M:%S}".format(
			datetime.datetime.strptime(name, "%Y%m%d-%H%M%S"))
		e.executionStarts(
			timestamp= timestamp,
			changelog=[])
		e.taskStarts(1,"First task")
		for i in xrange(ncommands) :
			e.commandStarts(1,i+1, "command {}".format(i+1))
			e.commandEnds(1,i+1,
				("output for command {}\n".format(i+1))*noutputlines,
				ok or i+1 != ncommands,
				info = None,
				stats=dict(param = int(name[-6:])) if stats and not i&3 else {})
		if running : return
		e.taskEnds(1,ok)
		e.executionEnds(ok)

	import os
	s = Server("fixture")
	os.system("rm -rf fixture")
	os.system("rm -rf www")
	s.createServer()
	s.now = datetime.datetime(2000,01,02,03,04,05)
	s.createProject("myproject")
	s.createClient("myproject", "client1")
	s.createClient("myproject", "client2")
	s.createClient("myproject", "client3")

	setUpExecution("client1", "20130304-050607",ncommands=3)
	setUpExecution("client1", "20130304-050608",ncommands=3, ntasks=3, stats=False)
	setUpExecution("client1", "20130305-050607",ncommands=4, ok=False, noutputlines=12)
	setUpExecution("client3", "20130304-050607",ncommands=4)
	setUpExecution("client3", "20130305-050607",ncommands=4, ok=False, running=True)
	s.clientIdle("myproject", "client1", 1)

	print "Starting generator"

	w = WebGenerator("www")
	w.generate(s)
	print w.generated









