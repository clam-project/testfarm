#! /usr/bin/python

import sys
sys.path.append('../src')
from task import *
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


os.environ['SVN_SSH']='ssh -i %s/.ssh/svn_id_dsa' % os.environ['HOME']

root_path = "$HOME/fingerprint-sandboxes/"
cd_root_path = "cd " + root_path

install_path = root_path + "local/"
cd_install_path = "cd " + install_path

songstamp_library_path = root_path + "clean-fingerprint/songstamp_library/trunk/"
cd_songstamp_library = "cd " + songstamp_library_path

songstamp_app_path = root_path + "clean-fingerprint/songstamp_app/trunk/"
cd_songstamp_app = "cd " + songstamp_app_path

songstamptest_path = root_path + "local/"
cd_songstamptest = "cd " + songstamptest_path

testdb_path = root_path + "test-db/"

fingerprint_path = root_path + "local/database/"
cd_fingerprint_path = "cd " + fingerprint_path

songstamp_update = 'svn update clean-fingerprint'
songstamp_checkout = 'svn checkout svn+ssh://testfarm@mtgdb.iua.upf.edu/fingerprint/ clean-fingerprint/'



HOME = os.environ['HOME']
os.environ['LD_LIBRARY_PATH']='%s/fingerprint-sandboxes/tlocal/lib:/usr/local/lib' % HOME


songstamp = Task(
	project_name="SongStamp", 
	client_name="testing_machine-linux_breezy", 
	task_name="with svn update" 
	)


songstamp.add_checking_for_new_commits( 
	checking_cmd='cd $HOME/fingerprint-sandboxes && svn status -u clean-fingerprint/ | grep \*', 
	minutes_idle=5
)

songstamp.add_deployment([
	"cd $HOME/",
	"mkdir -p fingerprint-sandboxes",
	"cd fingerprint-sandboxes",
#	"rm -rf clean-songstamp",
#
	songstamp_update,
#	songstamp_checkout,
#	{CMD : "svn diff --revision HEAD clean-songstamp/", INFO: pass_text},
#	{CMD : songstamp_checkout, INFO : pass_text },
] )


songstamp.add_subtask("build SongStamp core library", [
	cd_songstamp_library,
#	"scons benchmark=1 prefix=" + install_path,
	"scons benchmark=1 prefix=" + root_path + "songstamp-app-install",
] )	
	
songstamp.add_subtask("build SongStamp application", [
	cd_songstamp_app,
#	"scons benchmark=1 prefix=" + install_path,	
	"scons benchmark=1 prefix=" + root_path + "songstamp-app-install",	
	
] )


songstamp.add_subtask("copy data files to install path", [
#	cd_install_path,
	"cd " + root_path + "songstamp-app",
	"mkdir -p data",
	"mkdir -p database",	
	cd_root_path,
#	{CMD:"pwd && cd clean-fingerprint/", INFO: pass_text },
	"cp clean-fingerprint/data/aida4-models/model.bin local/data/",
] )


songstamp.add_subtask("clean-up database", [
	cd_fingerprint_path,
	"rm -f *.afp",
	"rm -f *.lst",
] )


#songstamp.add_subtask("SongStamp Extractor functional test ->  benchmark data", [
#	cd_songstamptest,
#	"bin/songstamp_app_extractor_benchmark data/model.bin " + testdb_path + "reference reference_audio_simple.lst database rebuild",
#] )


#songstamp.add_subtask("SongStamp Identifier functional test -> benchmark data", [
#	cd_songstamptest,
#	"bin/songstamp_app_identifier_benchmark data/model.bin database database_index.lst " + testdb_path + "user/dummy_22kHz_16bit_mono_simple.wav playlist.lst",
#] )


songstamp.add_subtask("build SongStamp core library for mobile gsm", [
	cd_songstamp_library,
	"scons mobile_gsm=1 prefix=" + root_path + "songstamp-daemon",
] )	

songstamp.add_subtask("build SongStamp daemon", [
	"cd " + root_path + "clean-fingerprint/songstamp_daemon/trunk/",
	"scons mobile_gsm=1 prefix=" + root_path + "songstamp-daemon",	
] )


Runner( songstamp, 
	continuous = True,
	remote_server_url = 'http://10.55.0.66/testfarm_server'
)
