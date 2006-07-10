#! /usr/bin/python

import sys
sys.path.append('../src')
from task import *
from project import Project
from client import Client
from runner import Runner


dollar_euro = Task( project = Project("Conversio"),
	client = Client("client_linux_dapper"),
	task_name = "compilacio del programa"
)

dollar_euro.add_subtask( "compilacio", [
	"cd $HOME/conversio",
	"g++ dollar2euro.cpp -o dollar2euro" 
	], 
	mandatory = True
)

dollar_euro.add_subtask( "un exemple: dollar a euro", [
	"cd $HOME/conversio",
	{CMD: "./dollar2euro 2", INFO: lambda x:x}
] )

dollar_euro.add_subtask( "dormir", ["sleep 3"])

Runner( dollar_euro, 
#	remote_server_url="http://localhost/testfarm_server",
	local_base_dir = "/tmp/localdir",	
	continuous=True
)
