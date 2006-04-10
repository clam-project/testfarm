#! /usr/bin/python

from os import environ

from testfarmclient import *

def pass_text(text) :
	return text


environ['SVN_SSH']='ssh -i %s/.ssh/svn_id_dsa' % environ['HOME']

cd_songstamp = "cd $HOME/songstamp-sandboxes/clean-songstamp/"
cd_songstamptest = "cd $HOME/songstamp-sandboxes/clean-songstamp/export/sdk-benchmark/example/"

songstamp_update = 'svn update clean-songstamp'

#songstampcheckout = 'svn checkout svn+ssh://testfarm@mtgdb.iua.upf.edu/fingerprint/songstamp/ clean-songstamp/'
songstamp_checkout = 'svn checkout svn+ssh://svn@mtgdb.iua.upf.edu/fingerprint/songstamp/ clean-songstamp/'


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
	"rm -rf clean-songstamp",
	songstamp_checkout,
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

songstamp.add_task("SongStamp Extractor functional test ->  benchmark data", [
	cd_songstamptest,
	"dir=`dirname $0`",
	#"export LD_LIBRARY_PATH=$dir/bin",
	#"echo $LD_LIBRARY_PATH",
	"$dir/bin/songstamp_extractor $dir/data/settings.bin $dir/audio/reference reference_audio.lst $dir/database interactive",
] )


songstamp.add_task("SongStamp Identifier functional test -> benchmark data", [
	cd_songstamptest,
	"dir=`dirname $0`",
	#"export LD_LIBRARY_PATH=$dir/bin",
	#"echo $LD_LIBRARY_PATH",
	"$dir/bin/songstamp_identifier $dir/data/settings.bin $dir/database database_index.lst $dir/audio/user/dummy_22kHz_16bit_mono.wav $dir/playlist.lst",
] )


TestFarmClient( 
	'lars linux breezy', 
	songstamp,  
	html_base_dir='./html',
	logs_base_dir='%s/songstamp-sandboxes/testfarm_logs' % environ['HOME'], #TODO can use $HOME ?
#	remote_server_url='http://10.55.0.66/testfarm_server',
	continuous=True 
)
