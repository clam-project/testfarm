How to install in a FastCGI environment with python-flup
========================================================

Remember that FastCGI is not the recommended setup.
The optimal one would be direct support of WSGI.

TO DOCUMENT

Virtual environment
-------------------

If you don't have access to the python installation you
can build a local virtual environment and install there
the packages you need.


	::bash
	export testfarmenv=~/testfarmenv # change it to whatever you need

	virtualenv $testfarmenv           # setups the Python environment
	. $testfarmenv/bin/activate       # activates it
	pip install virtualenv --upgrade  # upgrades it to the latest versiona

	# And testfarm server dependencies
	pip install webob
	pip install decorator

	# werkzeug-debugger has no pip install
	git clone git://github.com/daaku/werkzeug-debugger-appengine.git
	cd werkzeug-debugger-appengine
	python setup.py install


Installing server files
-----------------------

1. Ensure your Apache server has AllowOverrides enabled so
   you can use .htaccess files to override configuration.

2. Place '.htaccess' and 'dispatch.fcgi' files in this same
   folder into the folder in the configuration
		Note: .htaccess is, by naming, an invisible file
		it cannot be seen on 'ls' without the '-a' option
		and * don't match it.

3. Change in .htaccess the RewriteBase rule so that it matches
   the path for your service.

4. Edit the following variables on dispatch.fcgi



Installing dependencies
-----------------------










