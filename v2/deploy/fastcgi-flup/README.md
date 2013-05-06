How to install in a FastCGI environment with python-flup
========================================================

Remember that FastCGI is not the recommended setup.
The optimal one would be direct support of WSGI.

This configuration is useful when you have restrictions
on the hosting and you have no mod\_wsgi available
but you have some kind of FastCGI support.

Virtual environment
-------------------

If you don't have access to the python installation you
can build a local virtual environment and install there
the packages you need.

Define testfarmenv and src variables:

	export testfarmenv=~/testfarmenv  # virtual environment path
	export src=~/src                  # where to compile the sources
	mkdir -p $src

Create the virtual environment:

	virtualenv $testfarmenv           # setups the Python environment
	. $testfarmenv/bin/activate       # activates it
	pip install virtualenv --upgrade  # upgrades it to the latest versiona

Install TestFarm within the virtualenv

	cd $src
	git clone git://github.com/clam-project/testfarm.git
	cd $src/testfarm/v2
	python setup.py install

Install additional dependencies for flup mode

	pip install flup
	pip install werkzeug # just for the debugger

	# werkzeug-debugger has no pip install
	cd $src
	git clone git://github.com/daaku/werkzeug-debugger-appengine.git
	cd $src/werkzeug-debugger-appengine
	python setup.py install

Setup the log and the website
-----------------------------

Provided that:
* `~/testfarmlogs` is the path where you want to keep the logs
* `~/testfarmweb` is the path where you want to generate the testfarm website
* `MyProyect` is the first project you want to host
* `MyClient` is the first client you want to log

Then the usual initialization for a log.

	testfarmserver init ~/testfarmlogs

Test it:
	testfarmserver addproject ~/testfarmlogs MyProject
	testfarmserver addclient ~/testfarmlogs MyProject MyClient
	testfarmserver generate ~/testfarmlogs ~/testfarmweb

	testfarmserver fakerun ~/testfarmlogs MyProject MyClient
	testfarmserver generate ~/testfarmlogs ~/testfarmweb


Installing server files
-----------------------

1. Ensure your Apache server has AllowOverrides enabled so
   that you can use .htaccess files to override configuration.

2. Place '.htaccess' and 'dispatch.fcgi' files in this same
   folder into the folder in the configuration
		Note: .htaccess is, by naming, an invisible file
		it cannot be seen on 'ls' without the '-a' option
		and * don't match it.

3. Change in .htaccess the RewriteBase rule so that it matches
   the path for your service.

4. Edit the following variables on dispatch.fcgi

	* SERVICEPATH points to the path of the testfarmservice.py file
	* INTERP points to the python binary on your virtual environment
	* LOGPATH points to the logpath (~/testfarmlogs in the previous example)
	* WEBPATH points to the web (~/testfarmweb in the previous example)

5. Create a link to the fastcgi-flup path:

	cd $webroot
	ln -sf $src/testfarm/v2/deploy/fastcgi-flup/ testfarmserver

6. Create a link to the generated web:

	cd $webroot
	ln -sf ~/testfarmweb/MyProject testfarm










