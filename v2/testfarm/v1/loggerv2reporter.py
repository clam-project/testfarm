import datetime
from testfarm.logger import Logger

class LoggerV2Reporter(object) :
	"Adapter class for old clients to interact with v2 loggers"

	def __init__(self, logger, project, client) :
		self.logger = logger
		self.project = project
		self.client = client
		self.tasks = []
		self.subtasks = []
		self.commands = []

	def listen_found_new_commits( self, new_commits_found, seconds_idle ):
		self.logger.clientIdle(
			project = self.project,
			client = self.client,
			minutes=seconds_idle/60,
			)

	def listen_task_info(self, task):
		self.currentTask = task

	def listen_begin_task(self, taskname, snapshot=""):
		# TODO: what to do with taskname?
		taskname = "{:%Y%m%d-%H%M%S}".format(
			datetime.datetime.now())
		self.tasks.append(taskname)
		self.logger.executionStarts(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			snapshot=snapshot)

	def listen_begin_subtask(self, subtaskname):
		self.subtasks.append(subtaskname)
		self.subtaskok = True
		self.logger.taskStarts(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			task = len(self.subtasks),
			description = subtaskname,
			)

	def listen_begin_command(self, cmd):
		self.commands.append(cmd)
		self.logger.commandStarts(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			task = len(self.subtasks),
			command = len(self.commands),
			commandline = cmd)

	def listen_end_command(self, command, ok, output, info, stats):
		assert(self.commands)
		assert(command == self.commands[-1])
		self.logger.commandEnds(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			task = len(self.subtasks),
			command = len(self.commands),
			output = output,
			ok = ok,
			info = info or None,
			stats = stats,
			)
		self.commands.pop()
		self.subtaskok &= ok

	def listen_end_subtask(self, subtaskname) :
		assert(self.subtasks)
		assert(subtaskname == self.subtasks[-1])
		self.logger.taskEnds(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			task = len(self.subtasks),
			ok = self.subtaskok,
			)
		self.commands = []

	def listen_end_task(self, taskname, status):
		assert(self.tasks)
#		assert(taskname == self.tasks[-1])
		self.logger.executionEnds(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			ok = status,
			)
		self.commands = []
		self.subtasks = []
		self.currentTask = None

	def listen_end_task_gently(self, taskname):
		assert(self.tasks)
		assert(taskname == self.tasks[-1])
		self.logger.executionEnds(
			project = self.project,
			client = self.client,
			execution = self.tasks[-1],
			ok = None,
			)
		self.tasks = []
		self.subtasks = []
		self.commands = []
		self.currentTask = None





