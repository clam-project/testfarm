#!/usr/bin/python

import sys, os

DEBUG   = True
ROOT    = os.path.dirname(os.path.abspath(__file__))
ROOT    = '/home/dgarcia/testfarm/v2'
INTERP  = '/home/dgarcia/testfarmenv/bin/python'

# Ensure the interpret we are using is the one we want
if sys.executable != INTERP:
	os.execl(INTERP, INTERP, *sys.argv)

# testfarm in the module search path
sys.path.insert(1,ROOT+'/testfarm')
sys.path.insert(1,ROOT)

def application(environ, start_response):
	start_response('200 OK', [('Content-type', 'text/plain')])
	return ["Hello, world!\n"]+[repr(environ)]

import testfarm.service as service
application = service.Reload(service.Service(["testfarmservice"]))

if DEBUG:
	application.debug=True
	from werkzeug_debugger_appengine import get_debugged_app
	application = get_debugged_app(application)

if __name__ == '__main__':
	from flup.server.fcgi import WSGIServer
	WSGIServer(application).run()

