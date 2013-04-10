#!/usr/bin/env python

import os.path
from glob import glob
from distutils.core import setup

datapath='share/testfarm'
datafiles=[
#	'testfarm.cron',
#	'mod_python_testfarm.conf',
]+ glob("resources/*")

setup(
	name='testfarm',
	version='2.0',
	description = 'Testfarm, a continuous integration tool',
	url = 'http://github.com/clam-project/testfarm/',
	author = 'CLAM Project',
	author_email='info@clam-project.org',
	license = 'GPL v3 or later',
	packages = [
		'testfarm',
#		'testfarm_indicator',
		],
	package_dir = {
		'testfarm': 'testfarm',
#		'testfarm_indicator': 'indicator',
		},
	data_files=[ ( datapath, datafiles ), ],
	scripts = [
		"testfarmserver",
		],
	)


