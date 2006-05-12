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
slow_test = Project("slow test")
slow_test.brief_description = "a simple project with stupid slow tasks"

sleep_loop = Task(project = slow_test, client = linux_etch , task_name = "sleep loop")

sleep_loop.add_subtask("echo", ["echo hello"] )
sleep_loop.add_subtask("sleep 5 i 8 seconds", [{CMD:"sleep 7", INFO: print_some_info}, "sleep 8"] )
sleep_loop.add_subtask("incorrect command", ["lalala 5", "sleep 15"], mandatory = True )
sleep_loop.add_subtask("sleep 3 i 12 seconds", ["sleep 3", "sleep 12"] )

Runner( sleep_loop,
	continuous = True,
	local_base_dir = "local_dir"
 )
