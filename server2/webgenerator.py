
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


class WebGenerator(object) :
	def __init__(self, serverPath, webPath) :
		self.server = Server(serverPath)



	def executionDetails(self, project, client, execution) :
		executionSummary = self.server.execution(project, client, execution)
		executionInfo = self.server.executionInfo(project, client, execution)
		return detailsTemplate.format(
			project = project,
			client = client,
			execution = execution,
			deansi_style = deansi.styleSheet(),
			content = self.executionDetails_execution(executionSummary),
			)

	def executionDetails_execution(self, executionSummary) :
		return """\
<div class='execution'>
<h1>Details for execution '{execution}', started at {executionDate:%Y-%m-%d %H:%M:%S}</h1>
{taskcontent}
<p>Execution '{execution}' finalized at 2013-03-01 23:34:35</p>
<p>No errors detected</p>
</div>
""".format(
		execution = executionSummary.starttime,
		executionDate = datetime.datetime.strptime(
				executionSummary.starttime, "%Y%m%d-%H%M%S"),
		
		taskcontent = ""
		)
		

	def jsonSummary(self, project) :
		project_info = self.server.projectMetadata(project)
		content = [
				'{',
				'	"project" : "{}",'.format(project),
				'	"lastupdate" : "{:%Y/%m/%d %H:%M:%S}",'.format(
					datetime.datetime.now()),
				'	"clients" : [',
			] + [
				self.jsonClientSumary(project, client)
				for client in self.server.clients(project)
			] + [
				'	]',
				'}'
			]

	def jsonClientSumary(self, project, client) :
		clientInfo = self.server.clientMetadata(project, client)
		clientDescription = clientInfo['description']
		clientBriefDescription = clientInfo['briefDescription']

		executions = self.server.executions(project, client)

		idle_info = idle_per_client[client]
		current_task = None
		for name in reversed(executions) :
			status, start  = self.server
			log = self.server._logRead(project, client, executions)
			if status != 'inprogress' : break # found a finished task
			if current_task : continue # already have an inprogress task
			subtasks = self.__executed_subtasks(client, start)
			current_task = "Step %i: %s"%(
				len(subtasks),subtasks[-1]) if subtasks else "Starting up execution"

		status_map = {
			'broken': 'red',
			'stable': 'green',
			'aborted': 'int',
			'inprogress': 'int', # TODO: considering single inprogress execution
			}
		last_update = datetime.strptime(
			idle_info['date'], "%Y-%m-%d-%H-%M-%s")
		next_update = last_update + datetime.timedelta(
			seconds = idle_info['next_run_in_seconds'])
		failed_tasks = self.__failed_subtasks(client, start)

		doing = "run" if current_task else (
			"old" if next_update < datetime.datetime.now() else
			"wait"
			)
		content = [
			'		{',
			'			"name": "%s",' % client,
			'			"description": %s,' % repr(clientDescription),
			'			"name_details": \'%s\',' % clientBriefDescription,
			'			"status": "%s",'% status_map[status],
			'			"doing": "%s",' % doing,
			'			"lastupdate": "%s",' % format_date(last_update),
			] + ([
			'			"failedTasks":',
			'			[',
			] + [
			'				"%s",' % task
				for task in failed_tasks # todo
			] + [
			'			],',
			] if failed_tasks else []) + [
			'			stExecution": "%s",' % start,
			] + ([
			'			"currentTask": "%s",' % current_task,
			] if current_task else []) + [
			'		},',
			]


