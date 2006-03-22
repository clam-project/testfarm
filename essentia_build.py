#! /usr/bin/python

from os import environ

from testfarmclient import *

def pass_text(text) :
	return text

environ['SVN_SSH']='ssh -i %s/.ssh/svn_id_dsa' % environ['HOME']
cd_essentia = "cd $HOME/essentia-sandboxes/clean-essentia/trunk"

essentia_update = 'svn update svn+ssh://testfarm@mtgdb.iua.upf.edu/essentia/trunk/ clean-essentia/trunk/'

essentia_checkout = 'svn checkout svn+ssh://testfarm@mtgdb.iua.upf.edu/essentia/trunk/ clean-essentia/trunk/'

essentia = Repository("essentia/trunk")


essentia.add_task("TODO fix bug: update html at begin time ", [] )


essentia.add_checking_for_new_commits( 
	checking_cmd='cd $HOME/essentia-sandboxes && svn status -u clean-essentia/trunk | grep \*', 
	minutes_idle=5
)

essentia.add_deployment_task([
	"cd $HOME/",
	"mkdir -p essentia-sandboxes",
	"cd essentia-sandboxes",
	"rm -fr /tmp/essentia/",
	"rm -fr clean-essentia/trunk/build",
	"rm -fr clean-essentia/trunk/algorithms",
	"rm -fr clean-essentia/trunk/test/build",
	{CMD : "svn diff --revision HEAD clean-essentia/trunk", INFO: pass_text},
	{CMD : essentia_update, INFO : pass_text },
] )

essentia.add_task("build core libs", [
	cd_essentia,
	"scons base",
	"scons install base",
] )

essentia.add_task("build plugin libs", [
	cd_essentia,
	"scons",
	"scons install",
] )

essentia.add_task("automatic tests", [
	cd_essentia,
	"cd test",
	"scons",
	"cd build/unittests/descriptortests/",
	{CMD : "LD_LIBRARY_PATH=/tmp/essentia/lib/ ./test", INFO : pass_text},
] )



TestFarmClient( 'testing-machine_linux_breezy', [essentia],  use_pushing_server=True, continuous=True )
