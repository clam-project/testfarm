# encoding: utf-8
# Copyright © 2012-2013 David García Garzón and CLAM-project
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


from functools import partial
import os
import glob
import datetime

class BadServerPath(Exception) : pass
class ProjectNotFound (Exception) :
	def __init__(self, name) :
		super(ProjectNotFound, self).__init__(name)
		self.message = "Project not found '{}'".format(name)

class ClientNotFound (Exception) :
	def __init__(self, name) :
		super(ClientNotFound, self).__init__(name)
		self.message = "Client not found '{}'".format(name)

class ArgPrepender(object) :
	"""Wraps an object so that any method call to the wrapper,
	is delegated to the wrapped object but prepending the args
	provided on construction."""

	def __init__(self, wrapped, *args) :
		self.wrapped = wrapped
		self.args = args

	def __getattr__(self, name) :
		return partial(getattr(self.wrapped,name), *self.args)

class AttributeMap() :
	def __init__(self, **kwds) : self.update(**kwds)
	def __contains__(self, what) : return what in self.__dict__
	def update(self, **kwds) : return self.__dict__.update(**kwds)



class Server(object) :
	"""A server handles information from executions comming
	from several clients for several projects"""
	fileAccessTrace = []

	def __init__(self, path) :
		self._path = path
		self._now = None

	@property
	def now(self) :
		"""Holds the current time unless you set it to a concrete time"""
		if self._now : return self._now
		return datetime.datetime.now()
	@now.setter
	def now(self, value) :
		self._now = value

	def _p(self, *args) :
		return os.path.join(self._path, *args)

	def _assertPathOk(self) :
		if not os.path.isdir(self._path) :
			raise BadServerPath(self._path)

	def _assertProjectOk(self, project) :
		self._assertPathOk()
		if not os.path.isdir(self._p(project)) :
			raise ProjectNotFound(project)

	def _assertClientOk(self, project, client) :
		self._assertProjectOk(project)
		if not os.path.isdir(self._p(project, client)) :
			raise ClientNotFound(client)

	def _metadataUpdate(self, *args, **kwds) :
		filename = self._p(*args)
#		print "Updating meta",filename
		try : oldmeta = eval(open(filename).read())
		except IOError : oldmeta = {}
		oldmeta.update(kwds)
		metadata = open(self._p(*args),'w')
		metadata.write(repr(oldmeta))

	def _metadataRead(self, *args) :
		filename = self._p(*args)
#		print "Reading meta",filename
		try :
			return eval(open(filename).read())
		except IOError :
			return {}

	def _log(self, project, client, execution, *args) :
		log = self._logRead(project, client, execution)
		log.append(tuple(args))
		logfile = open(self._p(project, client, execution+".log"),'w')
		logfile.write(repr(log))

	def _logRead(self, project, client, execution) :
		filename = self._p(project, client, execution+".log")
#		print "Reading log ", filename
		try :
			return eval(open(filename).read())
		except IOError :
			return []

	def updateStats(self, project, client, execution, stats) :
		filename = self._p(project, client, "stats")
		f = open(filename, "a")
		for key, value in sorted(stats.iteritems()) :
			f.write(repr( (execution, key, value))+",\n")
		f.close()

	def clientStats(self, project, client) :
		filename = self._p(project, client, "stats")
		try :
			return eval("[" + open(filename).read() + "]")
		except IOError :
			return []
			
	def createServer(self) :
		os.mkdir(self._p())

	def createProject(self, project) :
		os.mkdir(self._p(project))
		self._metadataUpdate(project, "metadata")

	def createClient(self, project, client) :
		os.mkdir(self._p(project, client))
		self._metadataUpdate(project, client, "metadata")
		self.clientIdle(project, client, 0)

	def setProjectMetadata(self, project, **kwd) :
		self._metadataUpdate(project, "metadata", **kwd)

	def setClientMetadata(self, project, client, **kwd) :
		self._metadataUpdate(project, client, "metadata", **kwd)

	def projectMetadata(self, project) :
		return self._metadataRead(project, "metadata")

	def clientMetadata(self, project, client) :
		return self._metadataRead(project, client, "metadata")

	def executionInfo(self, project, client, execution) :
		return self._metadataRead(project, client, execution+".info")

	def projects(self) :
		return [
			project.split("/")[-2]
			for project in sorted(glob.glob(self._p("*","metadata")))
			]

	def clients(self, project) :
		return [
			project.split("/")[-2]
			for project in sorted(glob.glob(self._p(project,"*","metadata")))
			]

	def executions(self, project, client) :
		return [
			project.split("/")[-1][:-5]
			for project in sorted(glob.glob(self._p(project,client,"*.info")))
			]

	def executionStarts(self,
			project, client, execution,
			**kwds
			) :

		self._assertClientOk(project,client)
		self._metadataUpdate(project, client, execution+".info", **kwds)
		self._log(
			project, client, execution,
			"startExecution")


	def taskStarts(self,
			project, client, execution,
			task, description,
			) :

		self._assertClientOk(project,client)
		self._log(
			project, client, execution,
			"startTask", task, description)

	def commandStarts(self,
			project, client, execution,
			task, command, commandline
			) :

		self._assertClientOk(project,client)
		self._log(
			project, client, execution,
			"startCommand", task, command, commandline)

	def commandEnds(self,
			project, client, execution,
			task, command, output, ok, info, stats
			) :

		self._assertClientOk(project,client)
		self._log(project, client, execution,
			'endCommand', task, command, output, ok, info, stats)
		self.updateStats(project, client, execution, stats)

	def taskEnds(self,
			project, client, execution,
			task, ok,
			) :

		self._assertClientOk(project,client)
		self._log(
			project, client, execution,
			"endTask", task, ok)

	def executionEnds(self,
			project, client, execution,
			ok,
			) :

		self._assertClientOk(project,client)
		self._log(
			project, client, execution,
			"endExecution", ok, "{:%Y%m%d-%H%M%S}".format(self.now))

	def isRunning(self,
			project, client, execution=None) :

		if execution is None :
			executions = self.executions(project, client)
			if not executions : return False
			execution = executions[-1]

		log = self._logRead(project, client, execution)
		return not any([ "endExecution" in entry for entry in log])

	def clientStatus(self, project, client)  :
		executions = self.executions(project, client)
		if self.isRunning(project, client) :
			return "Running"
		expectedIdle = self.expectedIdle(project, client)
		if expectedIdle > self.now :
			return "Idle"
		return "NotResponding"


	def clientIdle(self, project, client, minutes) :
		self._assertClientOk(project,client)
		nextIdle = self.now + datetime.timedelta(minutes=minutes)
		idlefile = open(self._p(project,client,"idle"),'w')
		idlefile.write(nextIdle.strftime("%Y-%m-%d %H:%M:%S"))

	def expectedIdle(self, project, client) :
		filename = self._p(project,client,"idle")
#		print "Reading idle", filename
		return datetime.datetime.strptime(
			open(filename).read(),
			"%Y-%m-%d %H:%M:%S")



	def execution(self, project, client, execution) :
		"""Returns a Pythonic navegable structure with the information
		about an execution taken from its execution log"""

		summary = AttributeMap(
			failedTasks = [],
			running = True,
			tasks = [],
			)
		log = self._logRead(project, client, execution)
		tasks = {}
		commands = {}
		for entry in log :
			tag = entry[0]

			if tag == "startExecution":
				summary.starttime = execution
				continue

			if tag == "endExecution":
				summary.running = False
				summary.ok, summary.stoptime = entry[1:]
				continue

			if tag == "startTask":
				task, description = entry[1:]
				tasks[task] = AttributeMap(
					id = task,
					description=description,
					running = True,
					commands = [],
					)
				continue

			if tag == "endTask":
				task, ok = entry[1:]
				tasks[task].update(
					task = task,
					running = False,
					ok = ok,
					)
				continue

			if tag == "startCommand" :
				task, command, commandline = entry[1:]
				commands[task,command] = AttributeMap(
					id = command,
					task = task,
					commandline = commandline,
					running = True,
					)
				tasks[task].commands.append(commands[task,command])
				continue

			if tag == "endCommand" :
				task, command, output, ok, info, stats = entry[1:]
				commands[task,command].update(
					command = command,
					running = False,
					ok = ok,
					output = output,
					info = info,
					stats = stats,
					)
				continue


		summary.tasks = [task for id, task in sorted(tasks.iteritems())]

		summary.failedTasks = [
			(task.id, task.description)
			for task in summary.tasks
			if "ok" in task and not task.ok
			]

		if not summary.running :
			summary.ok &= not(summary.failedTasks)

		summary.currentTask = None
		if summary.tasks and summary.running :
			summary.currentTask = (
				summary.tasks[-1].id,
				summary.tasks[-1].description)

		return summary


	def client(self, project, client) :
		meta = AttributeMap(**self.clientMetadata(project, client))
		executions = self.executions(project, client)
		expectedIdle = self.expectedIdle(project, client)
		doing = "wait" if expectedIdle>self.now and executions else "old"

		data = AttributeMap(
			name = client,
			expectedIdle = expectedIdle,
			meta = meta,
			doing = doing,
			lastExecution = datetime.datetime(1900,1,1,0,0,0),
			currentTask = None,
			failedTasks = []
			)
		# TODO: If two running, the newer one remains
		for execution in  reversed(executions) :
			executionData = self.execution(project, client, execution)
			executionTime = datetime.datetime.strptime(execution,"%Y%m%d-%H%M%S")
			if executionData.running :
				data.currentTask = executionData.currentTask
				data.doing = 'run'
				data.runningSince = executionTime
				continue
			data.lastExecution = executionTime
			data.failedTasks = executionData.failedTasks
			data.ok = not data.failedTasks
			break
		data.status = "int" if "ok" not in data else 'green' if data.ok else "red"
		return data



