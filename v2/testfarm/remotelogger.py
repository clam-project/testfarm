
from serviceproxy import ServiceProxy
from serviceproxy import remote

class RemoteLogger(ServiceProxy) :

	def __init__(self, url) :
		super(RemoteLogger,self).__init__(url)
		pass

	@remote
	def clientIdle(self, project, client, minutes) : pass

	@remote
	def executionStarts(self, project, client, execution) : pass

	@remote
	def taskStarts(self, project, client, execution, task, description) : pass

	@remote
	def commandStarts(self, project, client, execution, task, command, commandline) : pass

	@remote
	def commandEnds(self, project, client, execution, task, command, output, ok, info, stats) : pass

	@remote
	def taskEnds(self, project, client, execution, task, ok) : pass

	@remote
	def executionEnds(self, project, client, execution, ok) : pass




