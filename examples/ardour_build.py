#! /usr/bin/python

import sys, os
from time import time

sys.path.append('../src')
from task import *
from runner import Runner

start_time = -1
def start_timer(output):
	global start_time
	start_time = time.time()

HOME = os.environ['HOME']
os.environ['LD_LIBRARY_PATH']='%s/clam-sandboxes/tlocal/lib:/usr/local/lib' % HOME


ardour2 = Task(
	project_name="ardour2",
	client_name="parumi_home_pc-linux_breezy",
	task_name="wget snapshot and compile"
	)
ardour2.add_deployment( [
	"cd",
	"cd src",
	{CMD:"pwd", INFO: lambda x:x},
	"rm ardour2-cvs*.bz2",
	"wget http://ardour.org/files/releases/ardour2-cvs.tar.bz2",
	"tar xjvf ardour2-cvs.tar.bz2",
	{INFO : start_timer}, 
	"scons PREFIX=../local", 
	{STATS : {'compile_time': time()-start_time} }, 
	"scons install"
	])

Runner( ardour2,
	local_base_dir = 'ardour_testfarm_files'
)
