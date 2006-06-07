#! /usr/bin/python

import sys
sys.path.append('../src')
from os import environ

from task import *
from project import Project
from client import Client
from runner import Runner
import os, time


start_time = -1
def start_timer(output):
	global start_time
	start_time = time.time()
def exectime_unittests(output):
	global start_time
	return {'exectime_unittests' : time.time() - start_time}
def exectime_functests(output):
	global start_time
	return {'exectime_functests' : time.time() - start_time}

def pass_text(text) :
	return text
	
def force_ok(text):
	return True


root_path = "d:\\sandbox\\fingerprint-sandboxes"
cd_root_path = "cd " + root_path

install_path = root_path + "\\local"
cd_install_path = "cd " + install_path

songstamp_library_path = root_path + "\\clean-fingerprint\\songstamp_library\\trunk"
cd_songstamp_library = "cd " + songstamp_library_path

songstamp_app_path = root_path + "\\clean-fingerprint\\songstamp_app\\trunk"
cd_songstamp_app = "cd " + songstamp_app_path

songstamptest_path = root_path + "\\local"
cd_songstamptest = "cd " + songstamptest_path

testdb_path = root_path + "\\test-db"

#fingerprint_path = root_path + "\\local\\database"
fingerprint_path = root_path + "\\local\\database"
cd_fingerprint_path = "cd " + fingerprint_path

songstamp_update = 'svn update svn+ssh://svn@mtgdb.iua.upf.edu/fingerprint/ clean-fingerprint'
songstamp_checkout = 'svn checkout svn+ssh://svn@mtgdb.iua.upf.edu/fingerprint/ clean-fingerprint'

windows = Client("testing_machine-windows_xp")
windows.brief_description = '<img src="http://clam.iua.upf.es/images/windows_icon.png"/>'

songstamp = Task(
	project = Project("SongStamp"), 
	client = windows, 
	task_name = "with svn update" 
	)

songstamp.set_check_for_new_commits( 
	#checking_cmd='cd root_path && svn status -u clean-fingerprint/ | grep \*', 
	checking_cmd='cd d:\\sandbox\\fingerprint-sandboxes && svn status -u clean-fingerprint | grep \*', 
	minutes_idle=5
)

songstamp.add_deployment([
	{CMD : "cd d:\\sandbox\\fingerprint-sandboxes", INFO : pass_text },
	{CMD : "mkdir clean-fingerprint", STATUS_OK : force_ok},	
	"cd clean-fingerprint",
	{CMD : songstamp_update, INFO : pass_text },
#	{CMD : songstamp_checkout, INFO : pass_text },
#	{CMD : "svn diff --revision HEAD clean-songstamp/", INFO: pass_text},
] )

songstamp.add_subtask("make install directory", [
	cd_root_path,
	{CMD : "mkdir songstamp-app-install", STATUS_OK : force_ok},
] )

songstamp.add_subtask("build SongStamp core library", [
	cd_songstamp_library,
	{CMD : "del options.cache", INFO : pass_text },
	"scons benchmark=1 prefix=" + root_path + "\\songstamp-app-install",
] )	
	
songstamp.add_subtask("build SongStamp application", [
	cd_songstamp_app,
	{CMD : "del options.cache", INFO : pass_text },	
	"scons benchmark=1 prefix=" + root_path + "\\songstamp-app-install",	
] )

songstamp.add_subtask("copy data files to install path", [
	cd_root_path,
	{CMD : "songstamp-app-install", STATUS_OK : force_ok},
	"cd songstamp-app-install",
	{CMD : "mkdir data", STATUS_OK : force_ok},
	{CMD : "mkdir database", STATUS_OK : force_ok},	
	cd_root_path,
	{CMD:"copy clean-fingerprint\\data\\aida4-models\\model.bin songstamp-app-install\\data", INFO: pass_text},
] )


songstamp.add_subtask("clean-up database", [
	{CMD : "cd d:\\sandbox\\fingerprint-sandboxes\songstamp-app-install", INFO : pass_text },	
	{CMD:"del /F *.afp", INFO: pass_text},	
	{CMD:"del /F *.lst", INFO: pass_text},		
] )

# Test: SongStampApp

songstamp.add_subtask("SongStamp Extractor functional test ->  benchmark data", [
	{CMD : "cd d:\\sandbox\\fingerprint-sandboxes\\songstamp-app-install", INFO : pass_text },	
#	cd_songstamptest,
	{CMD : "bin\\songstamp_app_extractor_benchmark data\\model.bin " + testdb_path + "\\reference reference_audio_simple.lst database rebuild", INFO : pass_text },
] )


songstamp.add_subtask("SongStamp Identifier functional test -> benchmark data", [
	{CMD : "cd d:\\sandbox\\fingerprint-sandboxes\\songstamp-app-install", INFO : pass_text },	
#cd_songstamptest,
	{CMD : "bin\\songstamp_app_identifier_benchmark data\\model.bin database database_index.lst " + testdb_path + "\\user\\dummy_22kHz_16bit_mono_simple.wav playlist.lst", INFO : pass_text },
] )

# Test: SongStampDaemon

#TODO: install ACE
#songstamp.add_subtask("make subdir for songstamp daemon install", [
#	cd_root_path,
#	{CMD : "mkdir songstamp-daemon-install", STATUS_OK : force_ok},	
#] )

#songstamp.add_subtask("build SongStamp core library for mobile gsm", [
#	cd_songstamp_library,
#	{CMD : "del options.cache", INFO : pass_text },	
#	"scons mobile_gsm=1 prefix=" + root_path + "\\songstamp-daemon-install",
#] )	

#songstamp.add_subtask("build SongStamp daemon", [
#	"cd " + root_path +"\\clean-fingerprint\\songstamp_daemon\\trunk",
#	{CMD : "del options.cache", INFO : pass_text },		
#	"scons mobile_gsm=1 prefix=" + root_path + "\\songstamp-daemon-install",	
#] )

# Test: SongStamp Training

# TODO: Install Essentia

#songstamp.add_subtask("make subdir for songstamp training install", [
#	cd_root_path,
#	{CMD : "mkdir songstamp-training-install", STATUS_OK : force_ok},		
##	"mkdir -p songstamp-training-install",
#] )

#songstamp.add_subtask("build SongStamp core library for training", [
#	cd_songstamp_library,
#	"scons training=1 prefix=" + root_path + "\\songstamp-training-install",
#] )

#songstamp.add_subtask("build SongStamp Training", [
#	"cd " + root_path + "clean-fingerprint\\songstamp_training\\trunk",
#	"scons training=1 prefix=" + root_path + "\\songstamp-training-install",
#] )

Runner( songstamp, 
	remote_server_url = 'http://10.55.0.66/testfarm_server',
	continuous = True,
#	local_base_dir = '/home/testfarmclient/fingerprint-sandboxes' 
)
