from testfarm.logger import Logger as _Logger
import os as _os
def _logger(request) :
	_path = request.environ.get("TESTFARM_LOGPATH", "projects")
	return _Logger(_path)

api = "2.0"

def clientIdle(request, project, client, minutes) :
	s = _logger(request)
	s.clientIdle(project, client, int(minutes))

def executionStarts(request, project, client, execution, **kwds) :
	s = _logger(request)
	s.executionStarts(project, client, execution, **kwds)

def taskStarts(request, project, client, execution, task, description) :
	s = _logger(request)
	s.taskStarts(project, client, execution, task, description)

def commandStarts(request, project, client, execution, task, command, commandline) :
	s = _logger(request)
	s.commandStarts( project, client, execution, task, command, commandline)

def commandEnds(request, project, client, execution,
		task, command, output, ok, info, stats
		) :
	s = _logger(request)
	s.commandEnds(project, client, execution,
		task, command, output, ok, info, stats
		)

def taskEnds(request, project, client, execution, task, ok) :
	s = _logger(request)
	s.taskEnds( project, client, execution, task, ok)

def executionEnds(request, project, client, execution, ok) :
	s = _logger(request)
	s.executionEnds( project, client, execution, ok)


