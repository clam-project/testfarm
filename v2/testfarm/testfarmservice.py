from testfarm.server import Server as _Server
_path = "projects"
_s = _Server(_path)

api = "2.0"

def clientIdle(project, client, minutes) :
	_s.clientIdle(project, client, int(minutes))

def executionStarts( project, client, execution) :
	_s.executionStars(project, client, execution)

def taskStarts( project, client, execution, task, description) :
	_s.taskStarts(project, client, execution, task, description)

def commandStarts( project, client, execution, task, command, commandline) :
	_s.commandStarts( project, client, execution, task, command, commandline)

def commandEnds(project, client, execution,
		task, command, output, ok, info, stats
		) :
	_s.commandEnds(project, client, execution,
		task, command, output, ok, info, stats
		)

def taskEnds( project, client, execution, task, ok) :
	_s.taskEnds( project, client, execution, task, ok)

def executionEnds( project, client, execution, ok) :
	_s.executionEnds( project, client, execution, ok)


