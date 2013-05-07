import os
import sys

def addIfNotInPath(path) :
	if path not in sys.path:
		sys.path.insert(0, path)

script_dir = os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"/../")
addIfNotInPath(scriptdir)

def application(environ, start_response):
	start_response('200 OK', [('Content-type', 'text/plain')])
	return ["Hello, world!\n"]+[repr(environ)]


import testfarm.service as service
application = service.Reload(service.Service(["testfarmservice"]))


