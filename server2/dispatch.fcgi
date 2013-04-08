#!/usr/bin/python

import sys, os

DEBUG   = True
ROOT    = os.path.dirname(os.path.abspath(__file__))
INTERP  = '/home/dgarcia/env/bin/python'

sys.path.insert(1,ROOT)
if sys.executable != INTERP:
   os.execl(INTERP, INTERP, *sys.argv)

import Server
application = Server.Reload(Server.Server("testfarmservice"))

if DEBUG:
   application.debug=True
   from werkzeug_debugger_appengine import get_debugged_app
   application = get_debugged_app(application)

if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(application).run()
