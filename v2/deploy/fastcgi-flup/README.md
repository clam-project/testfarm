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


	export testfarmenv=~/testfarmenv # change it to whatever you need

	virtualenv $testfarmenv           # setups the Python environment
	. $testfarmenv/bin/activate       # activates it
	pip install virtualenv --upgrade  # upgrades it to the latest version


Installing server files
-----------------------

1. Ensure your Apache server has AllowOverrides enabled so
   you can use .htaccess files to override configuration.

2. Place '.htacces' and 'dispatch.fcgi' files in this same
   folder into the folder in the configuration

3. Change in .htaccess the RewriteBase rule so that it matches
   the path for your service.

4. At this point you could use the dummy mode




Installing dependencies
-----------------------










