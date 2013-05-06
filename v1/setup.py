#!/usr/bin/env python

import os.path
from glob import glob
from distutils.core import setup

datafiles=[
	'testfarm.js',
	'testfarm.cron',
	'mod_python_testfarm.conf',
	'style.css',
	'summary.html',
]
datapath='share/testfarm'

setup(
	name='testfarm',
	version='1.0',
	description = 'Testfarm, a continuous integration tool',
#	home_page = 'http://sourceforge.net/projects/testfarm/',
	author = 'CLAM Project',
	author_email='info@clam-project.org',
	license = 'GPL v2 or later',
	packages = ['testfarm', 'testfarm_indicator'],
	package_dir = {
		'testfarm': 'src',
		'testfarm_indicator': 'indicator',
		},
	data_files=[ ( datapath, datafiles ), ],
	)


