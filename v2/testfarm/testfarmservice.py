from testfarm.server import Server as _Server
import os as _os
def _server(request) :
	print request.environ.keys()
	_path = request.environ.get("TESTFARM_LOGPATH", "projects")
	print "PATH", _path
	return _Server(_path)

api = "2.0"

def clientIdle(request, project, client, minutes) :
	s = _server(request)
	s.clientIdle(project, client, int(minutes))

def executionStarts( project, client, execution) :
	s = _server(request)
	s.executionStars(project, client, execution)

def taskStarts( project, client, execution, task, description) :
	s = _server(request)
	s.taskStarts(project, client, execution, task, description)

def commandStarts( project, client, execution, task, command, commandline) :
	s = _server(request)
	s.commandStarts( project, client, execution, task, command, commandline)

def commandEnds(project, client, execution,
		task, command, output, ok, info, stats
		) :
	s = _server(request)
	s.commandEnds(project, client, execution,
		task, command, output, ok, info, stats
		)

def taskEnds( project, client, execution, task, ok) :
	s = _server(request)
	s.taskEnds( project, client, execution, task, ok)

def executionEnds( project, client, execution, ok) :
	s = _server(request)
	s.executionEnds( project, client, execution, ok)


