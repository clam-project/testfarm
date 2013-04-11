#!/usr/bin/env python

import os.path
from glob import glob
from setuptools import setup, find_packages

datapath='share/testfarm'
datafiles=[
#	'testfarm.cron',
#	'mod_python_testfarm.conf',
]

setup(
	name='testfarm',
	version='2.0-dev',
	description = 'Testfarm, a continuous integration tool',
	url = 'http://github.com/clam-project/testfarm/',
	author = 'CLAM Project',
	author_email='info@clam-project.org',
	license = 'GPL v3 or later',
	install_requires = [
		'decorator',
		'webob',
		'argparse',
		'wsgi_intercept',
		'wsgiref',
		],
	packages = find_packages(),
	package_dir = {
		'testfarm': 'testfarm',
#		'testfarm_indicator': 'indicator',
		},
	data_files=[
		('resources', glob('resources/*' )),
		],
	test_suite = "runtest",
	scripts = [
		"testfarmserver",
		],
	)


