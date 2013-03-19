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



class Server(object) :
	"""A server handles information from executions comming
	from several clients for several projects"""

	def __init__(self, path) :
		self._path = path

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
		try : oldmeta = eval(open(self._p(*args)).read())
		except IOError : oldmeta = {}
		oldmeta.update(kwds)
		metadata = open(self._p(*args),'w')
		metadata.write(repr(oldmeta))

	def _metadataRead(self, *args) :
		try :
			return eval(open(self._p(*args)).read())
		except IOError :
			return {}

	def _log(self, project, client, execution, *args) :
		log = self._logRead(project, client, execution)
		log.append(tuple(args))
		logfile = open(self._p(project, client, execution+".log"),'w')
		logfile.write(repr(log))

	def _logRead(self, project, client, execution) :
		try :
			return eval(open(self._p(project, client, execution+".log")).read())
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

		self._log(
			project, client, execution,
			"startTask", task, description)

	def commandStarts(self,
			project, client, execution,
			task, sequence, command
			) :

		self._log(
			project, client, execution,
			"startCommand", task, sequence, command)

	def commandEnds(self,
			project, client, execution,
			task, command, output, ok, info, stats
			) :

		self._log(project, client, execution,
			'endCommand', task, command, output, ok, info, stats)

	def taskEnds(self,
			project, client, execution,
			task, ok,
			) :

		self._log(
			project, client, execution,
			"endTask", task, ok)

	def executionEnds(self,
			project, client, execution,
			ok
			) :

		self._log(
			project, client, execution,
			"endExecution", ok)

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
		if expectedIdle > datetime.datetime.now() :
			return "Idle"
		return "NotResponding"


	def clientIdle(self, project, client, minutes) :
		nextIdle = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
		idlefile = open(self._p(project,client,"idle"),'w')
		idlefile.write(nextIdle.strftime("%Y-%m-%d %H:%M:%S"))

	def expectedIdle(self, project, client) :
		return datetime.datetime.strptime(
			open(self._p(project,client,"idle")).read(),"%Y-%m-%d %H:%M:%S")



	def execution(self, project, client, execution) :
		class AttributeMap() :
			def __init__(self, **kwds) : self.update(**kwds)
			def __contains__(self, what) : return what in self.__dict__
			def update(self, **kwds) : return self.__dict__.update(**kwds)

		summary = AttributeMap(
			failedTasks = [],
			running = True,
			tasks = [],
			)
		log = self._logRead(project, client, execution)
		tasks = {}
		for entry in log :
			tag = entry[0]

			if tag == "startExecution":
				summary.starttime = execution
				continue

			if tag == "endExecution":
				summary.running = False
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

		summary.tasks = [task for id, task in sorted(tasks.iteritems())]
		if not summary.running : summary.ok = True

		summary.failedTasks = [
			(task.id, task.description)
			for task in summary.tasks
			if "ok" in task and not task.ok
			]

		summary.currentTask = None
		if summary.tasks and summary.running :
			summary.currentTask = (
				summary.tasks[-1].id,
				summary.tasks[-1].description)

		return summary

		if False :

			if tag is "startCommand" :
				task, command, commandline = entry[1:]
				tasks[task][command]=dict(
					commandline = commandline,
					running = True,
					)

			if tag is "endCommand" :
				task, command, output, status, info, stats = entry[1:]
				task[task][command].update(
					command = command,
					running = False,
					status = status,
					output = output,
					info = info,
					stats = stats,
					)



