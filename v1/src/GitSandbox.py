#!/usr/bin/python

import utils
import os.path

def debug(arg) :
	print "\033[33m",arg,"\033[0m"

class GitSandbox(object) :
	def __init__(self, sandbox ) :
		self.sandbox = sandbox

	# TODO: Not unit tested
	def location(self) :
		return self.sandbox

	def state(self) :
		return utils.output("cd %(sandbox)s && git  log --pretty=format:'%%H' -n 1 HEAD"%self.__dict__)

	def remoteState(self) :
		utils.run('cd %(sandbox)s && git fetch'%self.__dict__)
		return utils.output("cd %(sandbox)s && git  log --pretty=format:'%%H' -n 1 FETCH_HEAD"%self.__dict__)

	def update(self) :
		utils.run('cd %(sandbox)s && git stash'%self.__dict__)
		utils.run('cd %(sandbox)s && git pull'%self.__dict__)
		utils.run('cd %(sandbox)s && git stash pop || true'%self.__dict__)

	def pendingUpdates(self) :
		utils.run('cd %(sandbox)s && git fetch'%self.__dict__)
		output = utils.output('cd %(sandbox)s && git log --pretty=oneline HEAD..FETCH_HEAD'%self.__dict__)
		return [line.split()[0] for line in reversed(output.split('\n')) if line]

	def guilty(self) :
		utils.run('cd %(sandbox)s && git fetch'%self.__dict__)
		revisions = utils.output(
			('cd %(sandbox)s && '%self.__dict__)+
			'git log --pretty="format:%H\t%an <%ae>\t%s" HEAD...FETCH_HEAD'
			)
		return [
			tuple(revision.split('\t',2))
			for revision in reversed(revisions.split('\n'))
			if revision
			]

	def _pendingChanges(self) :
		utils.run('cd %(sandbox)s && git fetch'%self.__dict__)
		def listChanges(revisions) :
			return [
				line.split('\t')[::-1]
				for line in utils.output(
					('cd %(sandbox)s && '%self.__dict__)+
					'git diff --name-status %s'%revisions
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


