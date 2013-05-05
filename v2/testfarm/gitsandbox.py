#!/usr/bin/python

import utils
import os.path

def debug(arg) :
	print "\033[33m",arg,"\033[0m"

class GitSandbox(object) :
	def __init__(self, sandbox, verbose=False ) :
		self.sandbox = sandbox
		self._verbose = verbose

	def _run(self, command) :
		utils.run(
			command%self.__dict__,
			message = None if self._verbose else "",
			log = utils.null(),
			)

	def _output(self, command) :
		return utils.output(
			command%self.__dict__,
			message = None if self._verbose else "",
			)

	# TODO: Not unit tested
	def location(self) :
		return self.sandbox

	def state(self) :
		return self._output("cd %(sandbox)s && git  log --pretty=format:'%%H' -n 1 HEAD")

	def remoteState(self) :
		self._run('cd %(sandbox)s && git fetch')
		return self._output("cd %(sandbox)s && git  log --pretty=format:'%%H' -n 1 FETCH_HEAD")

	def update(self) :
		self._run('cd %(sandbox)s && git stash')
		self._run('cd %(sandbox)s && git pull')
		self._run('cd %(sandbox)s && git stash pop || true')

	def pendingUpdates(self) :
		self._run('cd %(sandbox)s && git fetch')
		output = self._output('cd %(sandbox)s && git log --pretty=oneline HEAD..FETCH_HEAD')
		return [line.split()[0] for line in reversed(output.split('\n')) if line]

	def guilty(self) :
		self._run('cd %(sandbox)s && git fetch')
		revisions = self._output(
			'cd %(sandbox)s && '
			'git log --pretty="format:%%H\t%%an <%%ae>\t%%s" HEAD...FETCH_HEAD'
			)
		return [
			tuple(revision.split('\t',2))
			for revision in reversed(revisions.split('\n'))
			if revision
			]

	def _pendingChanges(self) :
		self._run('cd %(sandbox)s && git fetch')
		def listChanges(revisions) :
			return [
				line.split('\t')[::-1]
				for line in self._output(
					'cd %(sandbox)s && '
					'git diff --name-status ' + revisions
					).splitlines()
				]
		originChanges = dict(listChanges("HEAD..FETCH_HEAD"))
		localChanges = dict(listChanges("HEAD"))
		cachedChanges = dict(listChanges("--cached"))
		output = dict([
			(file, ['none','none','none','none'])
			for file in  set(originChanges.keys() + localChanges.keys() + cachedChanges.keys())
			])

		for file, status in localChanges.iteritems() :
			if file in cachedChanges :
				output[file][0]= dict(
					A='added',
					D='deleted',
#					M='Mmodified', # No test case for it
					).get(status,status+cachedChanges[file]+"???")
			else :
				output[file][0]= dict(
#					A='Radded', # No test case for it
					D='missing',
					M='modified',
					).get(status,status+"???!")

		for file, status in originChanges.iteritems() :
			output[file][2]= dict(
				A='added',
				D='deleted',
				M='modified',
				).get(status,status+"???")
			if status in ('MD') :
				output[file][0] = 'normal'

		return [
			(os.path.join(self.sandbox,file), tuple(value))
			for file, value in sorted(output.iteritems())
			]

	def hasPendingChanges(self) :
		for path, (litem, lprop, ritem, rprop) in self._pendingChanges() :
			if litem == 'missing' : return True
			if ritem != 'none' : return True
			if rprop != 'none' : return True
		return False


