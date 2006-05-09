#! /usr/bin/python

import sys, os, time

sys.path.append('../src')
from task import *
from runner import Runner

start_time = -1
def start_timer(output):
	global start_time
	start_time = time.time()

HOME = os.environ['HOME']
os.environ['LD_LIBRARY_PATH']='%s/local/lib:/usr/local/lib' % HOME


ardour2 = Task(
	project_name="ardour2",
	client_name="parumi_home_pc-linux_breezy",
	task_name="wget snapshot and compile"
	)

ardour2.add_deployment( [
	"cd %s" % HOME,
	"cd src",
	{CMD:"pwd", INFO: lambda x:x},
	"rm ardour2-cvs*.bz2",
	"wget http://ardour.org/files/releases/ardour2-cvs.tar.bz2",
	"tar xjvf ardour2-cvs.tar.bz2",
	{INFO : start_timer}, 
	"cd ardour2",
	"scons PREFIX=%s/local" % HOME, 
	{STATS : {'compile_time': time.time()-start_time } }, 
	'scons install' ])

Runner( ardour2,
	local_base_dir = '%s/src/ardour_testfarm_files' % HOME
)
