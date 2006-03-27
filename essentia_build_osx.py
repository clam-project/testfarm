#! /usr/bin/python

from os import environ

from testfarmclient import *

def pass_text(text) :
	return text

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
	"scons base prefix=/tmp/essentia/",
	"scons install base prefix=/tmp/essentia/",
] )

essentia.add_task("build plugin libs", [
	cd_essentia,
	"scons prefix=/tmp/essentia",
	"scons install prefix=/tmp/essentia/",
] )

essentia.add_task("automatic tests", [
	cd_essentia,
	"cd test",
	"scons prefix=/tmp/essentia",
	"cd build/unittests/descriptortests/",
	{CMD : "DYLD_LIBRARY_PATH=/tmp/essentia/lib/ ./test", INFO : minicppunit_parser},
] )


TestFarmClient( 
	'testing-machine_linux_breezy', 
	essentia,  
	generated_html_path='./html',
	logs_path='%s/essentia-sandboxes/testfarm_logs' % environ['HOME'], #TODO can use $HOME ?
	continuous=True 
)
