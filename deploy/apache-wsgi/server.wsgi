import os
import sys

def addIfNotInPath(path) :
	if path not in sys.path:
		sys.path.insert(0, path)

script_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"/../")
path, package = os.path.split(script_dir)
addIfNotInPath(path)
addIfNotInPath('/home/vokimon/CajitasDeArena/testfarm/v2/')
addIfNotInPath('/home/vokimon/CajitasDeArena/testfarm/v2/testfarm')

print os.environ

def application(environ, start_response):
	start_response('200 OK', [('Content-type', 'text/plain')])
	return ["Hello, world!\n"]+[repr(environ)]


import testfarm.service as service
application = service.Reload(service.Service(["testfarmservice"]))


