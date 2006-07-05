#! /usr/bin/python

import sys
sys.path.append('../src')
from task import *
from project import Project
from client import Client
from runner import Runner

def num_warnings(output):
	warning_filter = lambda line : line.find('warning') != -1 or line.find('aviso') != -1
	result = filter(warning_filter, output.split('\n'))
	return {'num_warnings': len(result)}

dollar_euro = Task( project = Project("Conversio"),
	client = Client("client_linux_dapper"),
	task_name = "compilacio del programa"
)

#dollar_euro.set_check_for_new_commits(
#	checking_cmd="cd $HOME/conversion && cvs -nq up -dP | grep ^[UP]", 
#	minutes_idle=5
#)

dollar_euro.add_subtask( "compilacio", [
	"cd $HOME/conversio",
#	"cvs up",
	{CMD: "g++ dollar2euro.cpp -o dollar2euro", STATS: num_warnings},
	], 
	mandatory = True
)

dollar_euro.add_subtask( "un exemple: dollar a euro", [
	"cd $HOME/conversio",
	{CMD: "./dollar2euro 5", STATUS_OK: lambda x:float(x.split()[3])==3.98597}
] )

dollar_euro.add_subtask( "dormir", ["sleep 5"])

Runner( dollar_euro, 
#	remote_server_url="http://localhost/testfarm_server",
	local_base_dir = "/tmp",	
	continuous=True
)
