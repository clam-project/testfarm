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

modules = [
	os.path.splitext(os.path.basename(f))[0]
	for f in glob('src/*py')
	if "Test" not in f
	]

setup(name='bmaudio',
	version='1.0',
	description='Testfarm modules',
	author='CLAM Project',
	author_email='info@clam-project.org',
	packages = ['testfarm'],
	package_dir = {
		'testfarm': 'src',
		},
	data_files=[ ( datapath, datafiles ), ],
	)


