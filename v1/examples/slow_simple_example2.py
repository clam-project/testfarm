#! /usr/bin/python

import sys
sys.path.append('../src')
from task import *
from runner import Runner
from client import Client
from project import Project

print_some_info = lambda x: """some info some info some info some info some info some info some info some info some info some info 
some info some info some info some info some info some info some info some info some info some info some info some info 
some info some info some info some info some info some info some info some info some info some info some info some info 
some info some info some info some info some info some info some info some info some info some info some info some info 
some info some info some info some info some info some info some info some info some info some info some info some info 
""" 

linux_etch = Client("msordo_linux_etch")
linux_etch.brief_description = "linux etch brief description bla bla bla bla bla bla bla"
slow_test = Project("slow test")
logo = """\
<p> C++ library for audio and music: \
<a href="http://clam.iua.upf.edu">\
<img src="http://clam.iua.upf.edu/images/clamlogo.jpg"/>\
</a> project. </p>"""
slow_test.brief_description = logo

sleep_loop = Task(project = slow_test, client = linux_etch , task_name = "sleep loop")

sleep_loop.add_subtask("echo", ["echo hello"] )
sleep_loop.add_subtask("sleep 5 i 8 seconds", [{CMD:"sleep 7", INFO: print_some_info}, "sleep 8"] )
sleep_loop.add_subtask("incorrect command", ["lalala 5", "sleep 15"], mandatory = True )
sleep_loop.add_subtask("sleep 3 i 12 seconds", ["sleep 3", "sleep 12"] )

Runner( sleep_loop,
	continuous = True,
	local_base_dir = "local_dir"
 )
