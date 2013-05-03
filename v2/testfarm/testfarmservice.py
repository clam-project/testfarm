from testfarm.server import Server as _Server
import os as _os
import ast as _ast
def _server(request) :
	print request.environ.keys()
	_path = request.environ.get("TESTFARM_LOGPATH", "projects")
	print "PATH", _path
	return _Server(_path)

api = "2.0"

def clientIdle(request, project, client, minutes) :
	s = _server(request)
	s.clientIdle(project, client, int(minutes))

def executionStarts(request, project, client, execution, **kwds) :
	s = _server(request)
	kwds = { k:_ast.literal_eval(v) for k,v in kwds }
	s.executionStarts(project, client, execution, **kwds)

def taskStarts(request, project, client, execution, task, description) :
	s = _server(request)
	s.taskStarts(project, client, execution, task, description)

def commandStarts(request, project, client, execution, task, command, commandline) :
	s = _server(request)
	s.commandStarts( project, client, execution, task, command, commandline)

def commandEnds(request, project, client, execution,
		task, command, output, ok, info, stats
		) :
	s = _server(request)
	stats = _ast.literal_eval(stats)
	s.commandEnds(project, client, execution,
		task, command, output, ok, info, stats
		)

def taskEnds(request, project, client, execution, task, ok) :
	s = _server(request)
	s.taskEnds( project, client, execution, task, ok)

def executionEnds(request, project, client, execution, ok) :
	s = _server(request)
	s.executionEnds( project, client, execution, ok)


