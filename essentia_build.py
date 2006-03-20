#! /usr/bin/python

from testfarmclient import *

def pass_text(text) :
	return text

cd_essentia = "cd $HOME/essentia-sandboxes/clean-essentia/trunk"

essentia_update = "SVN_SSH=\"ssh -i $HOME/.ssh/svn_id_dsa\" svn update svn+ssh://testfarm@mtgdb.iua.upf.edu/essentia/trunk/ clean-essentia/trunk/"

essentia_checkout = "SVN_SSH=\"ssh -i $HOME/.ssh/svn_id_dsa\" svn checkout svn+ssh://testfarm@mtgdb.iua.upf.edu/essentia/trunk/ clean-essentia/trunk/"

essentia = Repository("essentia/trunk")

essentia.add_deployment_task([
	"cd $HOME/",
	"mkdir -p essentia-sandboxes",
	"cd essentia-sandboxes",
	"rm -fr /tmp/essentia/",
	"rm -fr clean-essentia/trunk/build",
	"rm -fr clean-essentia/trunk/algorithms",
	"rm -fr clean-essentia/trunk/test/build",
	essentia_update,
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


TestFarmClient( [essentia],  use_pushing_server=True, continuous=True )
