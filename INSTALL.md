Installing the library
======================

From the source path, use the provided setup.py script.

	python setup.py install

Or using the pip system:

	pip install testfarm


Installing the server
=====================

If you want to deploy a server receiving client reports,
documentation and configuration files for different
deployment methods are available at the 'deploy' directory.
The recommended setup is using mod_wsgi on Apache.


Deploying a client for local usage
==================================

Either if you want to install a server or run a client locally
you would like to deploy a log file structure.
This is done with the `testfarmserver` script.

This will initialize the a log structure:

	testfarmserver init ~/testfarmlogs

To create a new project:

	testfarmserver addproject ~/testfarmlogs MyProject
	# this sets the metadata
	testfarmserver meta ~/testfarmlogs MyProject \
		--set description 'My Project' \
		--set othermeta 'other value' \
		...

To allow clients to connect you have to add them first:

	testfarmserver addclient ~/testfarmlogs MyProject MyClient

You can test it by doing a fake run. See the help for options.

	testfarmserver fakerun ~/testfarmlogs MyProject MyClient

To generate the websites for all the projects:

	testfarmserver generate ~/testfarmlogs ~/testfarmweb



TODO:
-----

- create a client key
- configure your client
- configure your task specific id
- recommend having a sandbox
- recommend having a dedicated user
- recommend using local installs
- launching by hand
- cron jobs


