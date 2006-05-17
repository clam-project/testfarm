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
linux_breezy = Client("msordo_linux_breezy")
slow_test = Project("slow test")
logo = """\
<p> C++ library for audio and music: \
<a href="http://clam.iua.upf.edu">\
<img src="http://clam.iua.upf.edu/images/clamlogo.jpg"/>\
</a> project. </p>"""
slow_test.brief_description = logo

sleep_loop = Task(slow_test, linux_breezy, "task sleep loop")
sleep_loop.seconds_idle = 60

sleep_loop.add_subtask("echo", ["echo hello"] )
sleep_loop.add_subtask("sleep 5 i 8 seconds", [{CMD:"sleep 5", INFO: print_some_info}, "sleep 8"] )
sleep_loop.add_subtask("correct command", ["ls", "sleep 8"] )
sleep_loop.add_subtask("sleep 3 i 12 seconds", ["sleep 3", "sleep 12"] )


Runner( sleep_loop,
	continuous = True,
	#local_base_dir = 'local_dir'
	remote_server_url = 'http://localhost/testfarm_server'
 )
