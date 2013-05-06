
from logger import Logger
from logger import ArgPrepender
import deansi
import datetime
import os

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
						"togglesize('{0}');</script>\n".format(id),
				)
			)
	def command(self, command) :
		status = (
			"RUNNING" if command.running else
			"OK" if command.ok else "FAILED")
		indicatorclass = "command_"+(
			"running" if command.running else
			"ok" if command.ok else "failure")

		id  = "{0}_{1}".format(command.task, command.id)
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
						"		<b>{0}:</b> {1}<br />\n".format(param, value)
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

	def generate(self, logger, project, client, execution) :
		executionSummary = logger.execution(project, client, execution)
		executionInfo = logger.executionInfo(project, client, execution)
		return self.template.format(
			project = project,
			client = client,
			execution = execution,
			deansi_style = deansi.styleSheet(),
			content = ExecutionDetails().execution(executionSummary),
			)


class JsonSummary(object) :

	def client(self, logger, project, client) :
		data = logger.client(project, client)
		failedTasksBlock = '' if not data.failedTasks else (
			'			"failedTasks" : [\n' +
			''.join((
				'				"{0}",\n'.format(failedTask[1])
				for failedTask in data.failedTasks
			)) +
			'			],\n'
			)
		currentTaskBlock = '' if not data.currentTask else (
			'			"currentTask": "{0}",\n'.format(data.currentTask[1])
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
			'			"lastExecution": "{lastExecution:%Y%m%d-%H%M%S}",\n'
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

	def project(self, logger, project) :
		clientsBlock = "".join((
			self.client(logger, project, client)
			for client in logger.clients(project)
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
			now = logger.now,
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
<title>Testfarm: History for project {project} </title>
<link href="style.css" rel="stylesheet" type="text/css">
<script language="javascript" type="text/javascript" src="testfarm.js"></script>
<script language="javascript" type="text/javascript" src="jquery.js"></script>
<script language="javascript" type="text/javascript" src="https://www.google.com/jsapi"></script>
<script language="javascript" type="text/javascript" src="plot.js"></script>
</head>

<body class='history_page'>
<div id="theLayer" class="layer"></div>
<h1>
<a>TestFarm: History for project {project}
<span class='tooltip'>{description}</span>
<span class='description'>{briefDescription}</span>
</a>
</h1>
{content}
<div class="about">
<p>TestFarm is free software.
Learn <a href="http://testfarm.sf.net/">about TestFarm</a>.</p>
</div>
</body>
</html>
"""
	def execution(self, logger, project, client, execution) :
		data = logger.execution(project, client, execution)

		# TODO: briefDescription was named task_name in old testfarm
		# TODO: check where to really get it
		meta = logger.clientMetadata(project, client)
		try :
			briefDescription = meta["briefDescription"]
		except KeyError :
			briefDescription = "No brief description"

		starttime = datetime.datetime.strptime(
			data.starttime, "%Y%m%d-%H%M%S")
		status = "running" if data.running else "stable" if data.ok else "broken"
		endBlock = (
			"<div>in progress...</div>\n"
			if data.running else
			"<div><b>Finished:</b> {stoptime:%Y/%m/%d %H:%M:%S}</div>\n"
			.format(
				stoptime = datetime.datetime.strptime(
					data.stoptime, "%Y%m%d-%H%M%S"),
				)
			)
			
		return (
			'<a href="details-{client}-{execution}.html"\n'
			'	title="{Status}. Click to see the details"\n'
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


	def executionTable(self, logger, project) :
		clientsExecutions = dict( [
			( client, logger.executions(project, client))
			for client in logger.clients(project) ])

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
					self.execution(logger, project, client, execution)
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
				' src="{client}-stats.json"></div></a>'
			'</td>'
			).format(client = client.name)


	# TODO: Untested
	def generate(self, logger, project) :
		clients = [
			logger.client(project, client)
			for client in sorted(logger.clients(project))
			]
		meta = logger.projectMetadata(project)
		return self.template.format(
			project = project,
			description = meta.get('description',''),
			briefDescription = meta.get('briefDescription',''),
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
				+ self.executionTable(logger, project) +
				'</table>\n'
				)
		)


class ClientStatsPlot(object) :

	# TODO: no unit test for this
	def generate(self, logger, project, client) :
		stats = logger.clientStats(project, client)
		return self.tuplesToJson(stats)

	def tuplesToJson(self, data) :
		table = dict((
			((execution, key), value)
			for execution, key, value in data))
		execution = "20130301-010101"
		executions = self.executions(data)
		def formatedValueOrNul(execution, key) :
			try:
				return ', {0}'.format(table[execution,key])
			except KeyError:
				return ', null'

		return (
			'[\n'
			"[ 'Execution'"
			+ ''.join((
				', {0!r}'.format(key)
				for key in self.keys(data))) +
			' ],\n' +
			''.join((
				'[ {0!r}'.format(execution)
				+ ''.join((
					formatedValueOrNul(execution,key)
					for key in self.keys(data))) + ' ],\n'
				for execution in executions )) +
			']\n'
			)

	def keys(self, data) :
		return sorted(set(
			(( key for execution, key, value in data))))

	def executions(self, data) :
		return sorted(set(( execution for execution, key, value in data)))


statsPage = """\
<!DOCTYPE HTML>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="120">
<title>Testfarm History for project myproject </title>
<link href="style.css" rel="stylesheet" type="text/css">
<script language="javascript" type="text/javascript" src="testfarm.js"></script>
<script language="javascript" type="text/javascript" src="jquery.js"></script>
<script language="javascript" type="text/javascript" src="https://www.google.com/jsapi"></script>
<script language="javascript" type="text/javascript" src="plot.js"></script>
<style type="text/css">
html, body
{{
	height: 100%;
	}}
.plot
{{
	height: 90%;
	width: 100%;
}}
</style>
</head>

<body>
<h1>Stats for client '{client}'</h1>
<div class="plot" src="{client}-stats.json" />

<div class="about">
<p>TestFarm is free software.
Learn <a href="http://testfarm.sf.net/">about TestFarm</a>.</p>
</div>
</body>
</html>
"""

import pkg_resources

# TODO: Untested
class WebGenerator(object) :
	def __init__(self, target) :
		self.target = target
		self.generated = []

	def _p(self, *args) :
		return os.path.join(self.target, *args)

	def _mkdir(self, dir) :
		try : os.mkdir(dir)
		except OSError :
			if not os.access(dir, os.F_OK) :
				raise # not in there

	def copyToProject(self, project, file) :
		try :
			basepath = pkg_resources.Requirement.parse('testfarm')
			content = pkg_resources.resource_string(
				basepath,
				os.path.join('resources',file))
		except pkg_resources.DistributionNotFound as e :
			basepath = os.path.join(
				os.path.dirname(__file__),"..","resources",file)
			content = open(basepath).read()
		self.write(content, project, file)

	def write(self, content, *args) :
		filename = self._p(*args)
#		print "Writing",filename
		self.generated.append(filename)
		f = open(filename, 'w')
		f.write(content)
		f.close()

	def generate(self, logger) :
		self._mkdir(self._p())
		for project in logger.projects() :
			self.generateProject(logger, project)

	def generateProject(self, logger, project) :
		full = False
		self._mkdir(self._p(project))
		self.copyToProject(project, "style.css")
		self.copyToProject(project, "testfarm.js")
		self.copyToProject(project, "plot.js")
		self.copyToProject(project, "jquery.js")
		self.copyToProject(project, "summary.html")
		writer = ExecutionDetails()
		for client in logger.clients(project) :
			for execution in logger.executions(project, client) :
				self.write(writer.generate(logger,project,client,execution),
					project, "details-"+client+"-"+execution+".html")

			self.write(ClientStatsPlot().generate(logger,project, client),
				project, client+"-stats.json")
			self.write(statsPage.format(client=client),
				project, client+"-stats.html")

		writer = ProjectHistory()
		self.write(writer.generate(logger, project),
			project, "history.html")
		json = JsonSummary().project(logger, project)
		self.write(json,
			project,'testfarm-data.js')
		self.write("callme({0})".format(json),
			project, 'testfarm-data.jsond')

		self.write(writer.generate(logger, project),
			project, "history.html")

if __name__ == "__main__" :

	import sys
	if len(sys.argv) == 3 :
		s = Logger(sys.argv[1])
		w = WebGenerator(sys.argv[2])
		w.generate(s)
		sys.exit(0)
		

	def emulateExecution(client, name, tasks,
			project='myproject') :
		s = Logger("fixture")
		s = ArgPrepender(s, project, client, name)
		timestamp = "{0:%Y-%m-%d %H:%M:%S}".format(
			datetime.datetime.strptime(name, "%Y%m%d-%H%M%S"))
		s.executionStarts(
			timestamp=timestamp,
			changelog=[])
		for i, (task,commands) in enumerate(tasks) :
			s.taskStarts(i+1,task)
			for j, (line, ok, output, info, stats) in enumerate(commands) :
				s.commandStarts(i+1, j+1, line)
				if ok is None : return # Running or interrupted
				s.commandEnds(i+1, j+1,
					output=output,
					ok=ok,
					info=info,
					stats=stats)
				if ok is False : break # Failed, fatal for the task
			s.taskEnds(i+1,ok)
		s.executionEnds(ok)

	print "Simulating client calls"
	s = Logger("fixture")
	os.system("rm -rf fixture")
	os.system("rm -rf www")
	s.createServer()
	s.now = datetime.datetime(2000,01,02,03,04,05)
	s.createProject("myproject")
	s.createClient("myproject", "client1")
	s.createClient("myproject", "client2")
	s.createClient("myproject", "client3")

	emulateExecution("client1", "20130304-050607",[
		("first task", [
			("command 1", True, "output", None, dict(
				tests = 34,
			)),
		]),
	])
	emulateExecution("client1", "20130304-050608",[
		("first task", [
			("command 1", True, "output", "Info", dict(
				tests = 36,
			)),
			("command 2", True, "output", None, {}),
			("command 3", False, "output", None, {}),
		]),
	])
	emulateExecution("client1", "20130305-050607",[
		("Multi line outputs and info", [
			("command 1", True, "output\n"*12, "info\n"*12, dict(
				tests = 123,
				)),
			("command 2", True, "output\n"*12, "info\n"*12, {}),
			("command 3", False, "output\n"*12, None, {}),
		]),
	])
	emulateExecution("client3", "20130301-050607", [
		("Feeding stats", [
			("command 1", True, "output", "info", dict(
				tests = 325,
				loc = 424,
				)),
		]),
	])
	emulateExecution("client3", "20130302-050607", [
		("Feeding stats", [
			("command 1", True, "output", "info", dict(
				tests = 326,
				loc = 430,
				)),
		]),
	])
	emulateExecution("client3", "20130303-050607", [
		("Feeding stats", [
			("command 1", True, "output", "info", dict(
				tests = 336,
				loc = 450,
				)),
		]),
	])
	emulateExecution("client3", "20130304-050607", [
		("Example of incomplete task", [
			("command 1", True, "output\n"*12, "info\n"*12, dict(
				tests = 342,
				loc = 430,
				)),
			("command 2", True, "output\n"*12, "info\n"*12, {}),
			("command 3", True, "output\n"*12, None, {}),
		]),
	])
	emulateExecution("client3", "20130305-050607",[
		("Failing task that should not appear in red until execution finishes", [
			("command 1", True, "output", "info", {}),
			("command 2", False, "output", "info", {}),
		]),
		("Example of incomplete task", [
			("command 1", True, "output\n"*12, "info\n"*12, dict(
				tests = 442,
				loc = 530,
				)),
			("command 2", None, "output\n"*12, None, {}),
		]),
	])
	s.clientIdle("myproject", "client1", 1)

	print "Starting generator"
	w = WebGenerator("www")
	w.generate(s)
	print w.generated









