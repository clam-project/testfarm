#!/usr/bin/python

import sys, os

DEBUG   = True
SERVICEPATH = '/home/clamadm/testfarm/testfarm'
INTERP  = '/home/clamadm/testfarmenv/bin/python'
LOGPATH = '/home/clamadm/testfarmlogs/'

# Ensure the interpret we are using is the one we want
if sys.executable != INTERP:
	os.execl(INTERP, INTERP, *sys.argv)

# dummy application to test the launcher
def application(environ, start_response):
	start_response('200 OK', [('Content-type', 'text/plain')])
	return ["Hello, world!\n"]+[repr(environ)]

# testfarm service in the module search path
sys.path.insert(1,SERVICEPATH)

def createapp() :
       import testfarm.service as service
       application = service.Reload(service.Service(["testfarmservice"]))
       def wrapper(environ, start_response) :
               environ['TESTFARM_LOGPATH'] = LOGPATH
               return application(environ, start_response)
       return wrapper
application = createapp()

if DEBUG:
	application.debug=True
	from werkzeug_debugger_appengine import get_debugged_app
	application = get_debugged_app(application)

if __name__ == '__main__':
	from flup.server.fcgi import WSGIServer
	WSGIServer(application).run()



