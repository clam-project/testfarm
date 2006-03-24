#! /usr/bin/python

from os import environ
from testfarmclient import *

def pass_text(text) :
	return text

def force_ok(text):
	return True

def minicppunit_parser(text):
	result = []
	in_summary = False
	for line in text.split('\n'):
		if not in_summary and 'Summary:' in line:
			in_summary = True
			result.append( line )
		if in_summary :
			result.append( line )
		return "\n".join(result)

cd_essentia = "cd g:\\sandbox\\essentia-sandbox\\clean-essentia\\trunk\\"
essentia_update = '"c:\\program files\\svn\\svn" update svn+ssh://svn@mtgdb.iua.upf.edu/essentia/trunk/ clean-essentia/trunk/'
essentia_checkout = '"c:\\program files\\svn\\svn" checkout svn+ssh://svn@mtgdb.iua.upf.edu/essentia/trunk/ clean-essentia/trunk/'

essentia = Repository("essentia/trunk")

essentia.add_deployment_task([
	"cd g:\\sandbox\\",
	{CMD : "mkdir essentia-sandbox", STATUS_OK : force_ok},
	"cd essentia-sandbox",
	{CMD : "rmdir /S /Q C:\\usr\\include\\essentia", STATUS_OK : force_ok },
	{CMD : "del /Q C:\\usr\\lib\\essentia*", STATUS_OK : force_ok},
	{CMD : "rmdir /S /Q clean-essentia/trunk/build", STATUS_OK : force_ok},
	{CMD : "rmdir /S /Q clean-essentia/trunk/algorithms", STATUS_OK : force_ok},
	{CMD : "rmdir /S /Q clean-essentia/trunk/test/build", STATUS_OK : force_ok},
	#{CMD : '"c:/program files/svn/svn" diff --revision HEAD clean-essentia/trunk', INFO: pass_text},
	{CMD : essentia_checkout, INFO : pass_text },
] )

essentia.add_task("build core libs", [
	cd_essentia,
	"scons base mode=debug",
	"scons install base mode=debug",
] )

essentia.add_task("build plugin libs", [
	cd_essentia,
	"scons mode=debug",
	"scons install mode=debug",
] )

essentia.add_task("automatic tests", [
	cd_essentia,
	"cd test",
	"scons",
	"cd build/unittests/descriptortests/",
	{CMD : "test.exe", INFO : pass_text},
] )

TestFarmClient( 
	'testing-machine_windows', 
	[essentia],  
	generated_html_path='./html',
	logs_path='g:\\sandbox\\essentia-sandbox\\testfarm_logs',
	continuous=False 
)
