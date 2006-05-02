#! /usr/bin/python

import sys
sys.path.append('../src')
from os import environ

from testfarmclient import *

def pass_text(text) :
	return text


environ['SVN_SSH']='ssh -i %s/.ssh/svn_id_dsa' % environ['HOME']

songstamp_path = "$HOME/songstamp-sandboxes/clean-songstamp/"
cd_songstamp = "cd " + songstamp_path
songstamptest_path = "$HOME/songstamp-sandboxes/clean-songstamp/export/sdk-benchmark/example/"
cd_songstamptest = "cd " + songstamptest_path
testdb_path = "$HOME/songstamp-sandboxes/test-db/"
fingerprint_path = "$HOME/songstamp-sandboxes/clean-songstamp/export/sdk-benchmark/example/database/"
cd_fingerprint_path = "cd " + fingerprint_path

songstamp_update = 'svn update clean-songstamp'

#songstampcheckout = 'svn checkout svn+ssh://testfarm@mtgdb.iua.upf.edu/fingerprint/songstamp/ clean-songstamp/'
songstamp_checkout = 'svn checkout svn+ssh://testfarm@mtgdb.iua.upf.edu/fingerprint/songstamp/ clean-songstamp/'


songstamp = Repository("songstamp")

#songstamp.add_task("TODO fix bug: update html at begin time ", [] )

songstamp.add_checking_for_new_commits( 
	checking_cmd='cd $HOME/songstamp-sandboxes && svn status -u clean-songstamp/ | grep \*', 
	minutes_idle=5
)

songstamp.add_deployment_task([
	"cd $HOME/",
	"mkdir -p songstamp-sandboxes",
	"cd songstamp-sandboxes",
#	"rm -rf clean-songstamp",
#
	songstamp_update,
#	songstamp_checkout,
#	{CMD : "svn diff --revision HEAD clean-songstamp/", INFO: pass_text},
#	{CMD : songstamp_checkout, INFO : pass_text },
] )

songstamp.add_task("build core library", [
	cd_songstamp,
	"scons static=1 benchmark=1",
] )


if sys.platform == "linux2":
        lib_path = "LD_LIBRARY_PATH"
        machine = "testing-machine_linux_breezy"
elif sys.platform == "darwin":
        lib_path = "DYLD_LIBRARY_PATH"
        machine = "testing_machine_osx_tiger"


# do test of the exported sonsstamp library

songstamp.add_task("copy core files to export directory", [
	cd_songstamp,
	"cp src/libsongstamp/songstamp_api/SongStampDemo.h export/sdk-benchmark/include",
	"cp lib/libsongstamp.a export/sdk-benchmark/lib",
	"cp /usr/lib/libsndfile.a export/sdk-benchmark/lib",
	"cp data/settings.bin export/sdk-benchmark/example/data",
	"cp doc/BMAT-SongStamp-Demo-SDK-Documentation.pdf export/sdk-benchmark/doc",
] )


songstamp.add_task("build executables linked to the exported core library", [
	cd_songstamptest,
	"scons",
] )

songstamp.add_task("clean-up database", [
	cd_fingerprint_path,
	"rm -f *.afp",
	"rm -f *.lst",
] )

songstamp.add_task("SongStamp Extractor functional test ->  benchmark data", [
	cd_songstamptest,
	#"bin/songstamp_extractor data/settings.bin testdb_path/reference reference_audio.lst database interactive",
	"bin/songstamp_extractor data/settings.bin " + testdb_path + "reference reference_audio_simple.lst database rebuild",
] )


songstamp.add_task("SongStamp Identifier functional test -> benchmark data", [
	cd_songstamptest,
	"bin/songstamp_identifier data/settings.bin database database_index.lst " + testdb_path + "user/dummy_22kHz_16bit_mono_simple.wav playlist.lst",
] )


TestFarmClient( 
	'testing-machine_linux_breezy', 
	songstamp,  
#	html_base_dir='./html',
#	logs_base_dir='%s/songstamp-sandboxes/testfarm_logs' % environ['HOME'], #TODO can use $HOME ?
	remote_server_url='http://10.55.0.66/testfarm_server',
	continuous=True 
)
