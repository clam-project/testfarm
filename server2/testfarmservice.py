from server import Server
path = "projects"
s = Server(path)

def clientIdle(project, client, minutes) :
	import datetime
	s.clientIdle(project, client, int(minutes))

def executionStarts( project, client, execution) :
	s.executionStars(project, client, execution)

def taskStarts( project, client, execution, task, description) :
	s.taskStarts(project, client, execution, task, description)

def commandStarts( project, client, execution, task, command, commandline) :
	s.commandStarts( project, client, execution, task, command, commandline)

def commandEnds(project, client, execution,
		task, command, output, ok, info, stats
		) :
	s.commandEnds(project, client, execution,
		task, command, output, ok, info, stats
		)

def taskEnds( project, client, execution, task, ok) :
	s.taskEnds( project, client, execution, task, ok)

def executionEnds( project, client, execution, ok) :
	s.executionEnds( project, client, execution, ok)


