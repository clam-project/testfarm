#! /usr/bin/python

# this is a testfarm client for testing testfarm itself

# to install as a cron script, use this line in crontab
# 0,5,10,15,20,25,30,35,40,45,50,55 * * * *    (cd /home/testfarm/testfarm/v2/ && git pull && ./runOnce.py lock ./client_selftest.py) 2>&1 | cat > /tmp/err_testfarm_testfarm


import os, sys, time
sys.path.append('%s/testfarm/v2' % os.environ['HOME'])
from testfarm.v1.task import Task, CMD, INFO, STATS, CD, STATUS_OK
from testfarm.v1.project import Project
from testfarm.v1.client import Client
from testfarm.v1.runner import Runner
from testfarm.utils import loadDictFile
from testfarm.v1.mailreporter import MailReporter
from testfarm.v1.ircreporter import IrcReporter
from commands import getoutput
from testfarm.v1.GitSandbox import GitSandbox
import re

startTime = -1
def startTimer():
	global startTime
	startTime = time.time()
def ellapsedTime():
	global startTime
	return time.time() - startTime
def countLines( path ):
	print 'loc for path:', path
	# /dev/null is to be safe when no files match
	output = getoutput("cat /dev/null $(find {} -name '*.py') | wc -l"
			.format(path.strip())
			)
	return int(output)
def pyunitTestCount(output) :
	m = re.search(r"Ran (?P<unittests>[0-9]+) tests", output)
	if m is None : return {}
	return dict(unittests=int(m.group("unittests")))


localDefinitions = dict(
	description= 
		'<img src="http://clam-project.org/images/linux_icon.png"/>\n'
		'<img src="http://clam-project.org/images/ubuntu_icon.png"/>\n',
	sandbox= os.path.expanduser('~/'),
)
try :
	localDefinitions.update(loadDictFile(os.path.expanduser('~/.config/testfarm/testfarm')))
	localDefinitions['name'] # ensure that name is defined
	localDefinitions['description']
except :
	print >> sys.stderr, "ERROR: You should create ~/.config/testfarmrc with at least the name and description attributes of your client"
	raise

localDefinitions['installPath'] = os.path.join(localDefinitions['sandbox'],"local")
#os.environ['LD_LIBRARY_PATH']='%(installPath)s/lib:/usr/local/lib' %localDefinitions
#os.environ['PATH']=':'.join([
#	'%(installPath)s/bin'% localDefinitions,
#	os.path.expanduser('~/bin'), # for soxsucks
#	os.environ['PATH'],
#	])
os.environ['PYTHONPATH']='%(installPath)s/lib/python' % localDefinitions

client = Client(localDefinitions['name'])
client.brief_description = localDefinitions['description']

clam = Task(
	project = Project('CLAM','<a href="http://clam-project.org">clam web</a>' ),
	client = client,
	task_name='Testfarm',
	)

clam.add_sandbox(GitSandbox(os.path.join(localDefinitions['sandbox'], 'testfarm')))

clam.set_check_for_new_commits(
	checking_cmd = 'false'%localDefinitions,
	minutes_idle = 15,
)

clam.add_subtask('count lines of code', [
	{CMD:'echo %(sandbox)s/testfarm/src'%localDefinitions, STATS: lambda x: {'testfarm_v1_loc': countLines(x) } },
	{CMD:'echo %(sandbox)s/testfarm/v2'%localDefinitions, STATS: lambda x: {'testfarm_v2_loc': countLines(x) } },
] )

clam.add_deployment( [
	'cd %(sandbox)s/testfarm/v2'%localDefinitions,
	'rm $(find -name \'*.pyc\')',
] )

clam.add_subtask('Unit Tests', [
	'cd %(sandbox)s/testfarm/v2'%localDefinitions,
	{INFO : lambda x:startTimer() },
	{CMD : './runtest.py', STATS : pyunitTestCount, },
	{STATS : lambda x:{'exectime_unittests' : ellapsedTime()} },
] )

forceRun = len(sys.argv)>1
print "force Run: ", forceRun

extra_listeners = []

if 'mail_report' in localDefinitions :
	mail_report_args = localDefinitions['mail_report'].__dict__
	del mail_report_args["__module__"]
	del mail_report_args["__doc__"]
	extra_listeners.append(
		MailReporter(
			testfarm_page="http://clam-project.org/testfarm.html",
			**mail_report_args))

if 'irc_report' in localDefinitions :
	irc_report_args = localDefinitions['irc_report'].__dict__
	del irc_report_args["__module__"]
	del irc_report_args["__doc__"]
	extra_listeners.append(
		IrcReporter(
			testfarm_page="http://clam-project.org/testfarm.html",
			**irc_report_args))

try:
	from testfarm.v1.loggerv2reporter import LoggerV2Reporter
	from testfarm.logger import Logger
	from testfarm.remotelogger import RemoteLogger
	extra_listeners.append(
		LoggerV2Reporter(
			RemoteLogger("http://localhost/testfarm/server/testfarmservice"),
#			Logger(os.path.expanduser("~/logs/")),
			"CLAM",
			localDefinitions['name'],
		)
	)
except ImportError as e:
	print >> sys.stderr, "Testfarm server v2 not available"
	raise

Runner( clam, 
	continuous = False,
	first_run_always = forceRun,
#	remote_server_url = 'http://84.88.76.92/testfarm_server',
#	local_base_dir='/tmp',
	extra_listeners = extra_listeners,
)

