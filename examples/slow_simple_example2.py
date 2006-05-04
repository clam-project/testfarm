#! /usr/bin/python

import sys
sys.path.append('../src')
from testfarmclient import *

for_loop = Repository("slow test")

print_some_info = lambda x: """some info some info some info some info some info some info some info some info some info some info 
some info some info some info some info some info some info some info some info some info some info some info some info 
some info some info some info some info some info some info some info some info some info some info some info some info 
some info some info some info some info some info some info some info some info some info some info some info some info 
some info some info some info some info some info some info some info some info some info some info some info some info 
""" 

for_loop.add_task("echo", ["echo hello"] )
for_loop.add_task("sleep 5 i 20 seconds", [{CMD:"sleep 7", INFO: print_some_info}, "sleep 20"] )
for_loop.add_task("incorrect command", ["lalala 5", "sleep 15"], mandatory = True )
for_loop.add_task("sleep 3 i 12 seconds", ["sleep 3", "sleep 12"] )



TestFarmClient( "msordo2_linux_breezy", 
		for_loop,
		continuous = True,
		html_base_dir = "html2",
		logs_base_dir = "html2-logs"
 )
