from server import Server

class ServerReporter(object) :

	def __init__(self, server, project, client) :
		self.server = server
		self.project = project
		self.client = client
		self.tasks = []
		self.subtasks = []
		self.commands = []

	def listen_found_new_commits( self, new_commits_found, seconds_idle ):
		self.server.clientIdle(
			project = self.project,
			client = self.client,
			minutes=seconds_idle/60,
			)

	def listen_task_info(self, task):
		self.currentTask = task

	def listen_begin_task(self, taskname, snapshot=""):
		self.tasks.append(taskname)
		self.server.executionStarts(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			snapshot=snapshot)

	def listen_begin_subtask(self, subtaskname):
		self.subtasks.append(subtaskname)
		self.server.taskStarts(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			task = len(self.subtasks),
			description = subtaskname,
			)

	def listen_begin_command(self, cmd):
		self.commands.append(cmd)
		self.server.commandStarts(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			task = len(self.subtasks),
			command = len(self.commands),
			commandline = cmd)

	def listen_end_command(self, command, ok, output, info, stats):
		assert(self.commands)
		assert(command == self.commands[-1])
		self.server.commandEnds(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			task = len(self.subtasks),
			command = len(self.commands),
			output = output,
			ok = ok,
			info = info,
			stats = stats,
			)
		self.commands.pop()

	def listen_end_subtask(self, subtaskname) :
		assert(self.subtasks)
		assert(subtaskname == self.subtasks[-1])
		self.server.taskEnds(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			task = len(self.subtasks),
			ok = True, # TODO: ok=True????
			)
		self.subtasks.pop()

	def listen_end_task(self, taskname, status):
		assert(self.tasks)
		assert(taskname == self.tasks[-1])
		self.server.executionEnds(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			ok = status,
			)
		self.tasks.pop()
		self.currentTask = None

	def listen_end_task_gently(self, taskname):
		assert(self.tasks)
		assert(taskname == self.tasks[-1])
		self.server.executionEnds(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			ok = None,
			)
		self.tasks = []
		self.subtasks = []
		self.commands = []
		self.currentTask = None





