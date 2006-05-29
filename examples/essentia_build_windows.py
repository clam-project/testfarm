#! /usr/bin/python

import sys
sys.path.append('../src')
from os import environ

from task import *
from client import Client
from project import Project
from runner import Runner

def pass_text(text) :
	return text

def force_ok(text):
	return True

cd_essentia = "cd g:\\sandbox\\essentia-sandbox\\clean-essentia\\trunk"
essentia_update = '"c:\\program files\\svn\\svn" update svn+ssh://svn@mtgdb.iua.upf.edu/essentia/trunk/ clean-essentia\\trunk'
essentia_checkout = '"c:\\program files\\svn\\svn" checkout svn+ssh://svn@mtgdb.iua.upf.edu/essentia/trunk/ clean-essentia\\trunk'

windows = Client("windows")
windows.brief_description = '<img src="http://clam.iua.upf.es/images/windows.png"/>'

essentia = Task(
			project = Project("essentia_trunk"),
			client = windows,
			task_name = "doing a chechout" 
		)
		
'''
essentia.set_check_for_new_commits( 
	checking_cmd='cd g:\\sandbox\\essentia-sandbox && "c:\\program files\\svn\\svn" status -u clean-essentia\\trunk | grep \*', 
	minutes_idle=5
)
'''

essentia.add_deployment([
	"cd g:\\sandbox",
	{CMD : "mkdir essentia-sandbox", STATUS_OK : force_ok},
	"cd essentia-sandbox",
	{CMD : "rmdir \\S \\Q C:\\usr\\include\\essentia", STATUS_OK : force_ok },
	{CMD : "del \\Q C:\\usr\\lib\\essentia*", STATUS_OK : force_ok},
	{CMD : "rmdir \\S \\Q clean-essentia\\trunk\\build", STATUS_OK : force_ok},
	{CMD : "rmdir \\S \\Q clean-essentia\\trunk\\algorithms", STATUS_OK : force_ok},
	{CMD : "rmdir \\S \\Q clean-essentia\\trunk\\test\\build", STATUS_OK : force_ok},
	{CMD : essentia_checkout, INFO : pass_text },
])

essentia.add_subtask("build core libs", [
	cd_essentia,
	"scons base mode=debug",
	"scons install base mode=debug",
])

essentia.add_subtask("build plugin libs", [
	cd_essentia,
	"scons mode=debug",
	"scons install mode=debug",
])

essentia.add_subtask("automatic tests", [
	cd_essentia,
	"cd test",
	"scons",
	"cd build\\unittests\\descriptortests",
	{CMD : "test.exe", INFO : pass_text},
])

Runner ( 
	essentia,  
	remote_server_url='http://10.55.0.66/testfarm_server',
	continuous=False 
)
