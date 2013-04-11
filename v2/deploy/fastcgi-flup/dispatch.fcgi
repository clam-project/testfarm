#!/usr/bin/python

import sys, os

DEBUG   = False
ROOT    = os.path.dirname(os.path.abspath(__file__))
#INTERP  = '/home/dgarcia/env/bin/python'
INTERP  = '/usr/bin/python'

sys.path.insert(1,ROOT)
if sys.executable != INTERP:
	os.execl(INTERP, INTERP, *sys.argv)

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

