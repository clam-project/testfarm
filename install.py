#! /usr/bin/python

import sys, os, shutil
from errno import errorcode

PYTHON_NEEDED_VERSION = "python2.4"
PYTHON_VERSION = ""
TESTFARM_DIR = ""
verbose = False

############################################### USER-DEFINED EXCEPTION ############################################

class CommandError:
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg


################################################## PRINT VERBOSITY ################################################

def print_verbose(msg):
	if verbose:
		sys.stdout.write(msg) 

###################### CHECK THAT THE PYTHON VERSION INSTALLED IS GREATER THAN OR EQUAL TO 2.4 ####################

def check_installed_python():
	print_verbose("checking installed python version ... ")
	
	global PYTHON_VERSION
	PYTHON_VERSION = "python%s.%s" % ( sys.version_info[0], sys.version_info[1] )
	if PYTHON_VERSION < PYTHON_NEEDED_VERSION :
		print_verbose(" [Fail]\n")
		raise CommandError, "ERROR, '%s' version was found, but Python 2.4 or greater is needed" % PYTHON_VERSION
	
	print_verbose("%s [OK]\n" % PYTHON_VERSION)

#################################### CREATE DIRS IN SITE-PACKAGES AND COPY FILES ##################################

def do_create_dirs_and_copy_files():
	print_verbose("checking operating system ... ")
	global TESTFARM_DIR
	if sys.platform == 'win32' :
		print_verbose("Win32-like system\n")
		site_packages = "%s\lib\site-packages" % sys.prefix
		TESTFARM_DIR = "%s\\testfarm" % site_packages
	else :
		print_verbose("Unix-like system\n")
		site_packages = "%s/lib/%s/site-packages" % ( sys.prefix, PYTHON_VERSION )
		TESTFARM_DIR = "%s/testfarm" % site_packages

	try:
		print_verbose("creating tesfarm directory at %s ... " % TESTFARM_DIR)
		os.mkdir( TESTFARM_DIR ) # this command needs ROOT privileges
	except OSError, oserror:
		if errorcode[oserror.errno] == 'EEXIST': 
			print_verbose( oserror.strerror )
		else:
			print_verbose( " [Fail]\n")
			raise CommandError, oserror.strerror
	print_verbose(" [OK]\n")
	
	print_verbose("copying files to '%s' dir ... " % TESTFARM_DIR)
	ls = os.listdir('src')
#	python_files_filter = lambda entry : len(entry.split('.')) >= 2 and entry.split('.')[len(entry.split('.'))-1] == 'py' 
#	filenames = filter(python_files_filter, ls)
	try:
		count = 0
		for entry in ls:
			splitted_entry = entry.split('.')
			if len(splitted_entry) >= 2 and splitted_entry[len(splitted_entry)-1] == 'py':
				filename = '.'.join(splitted_entry)
				shutil.copy('src/%s' % filename, TESTFARM_DIR) # this command needs ROOT privileges
				count += 1
		print_verbose(" copied %s files [OK]\n" %count)
	except IOError, ioerror:
			print_verbose( " [Fail]\n")
			raise CommandError, ioerror.strerror	
		
######################################################### MAIN ####################################################

try: 
	if sys.argv[1] == '--verbose':
		verbose = True
	elif sys.argv[1] == '--help':
		print "NAME"
		print "\tTestfarm installer.\n"
		print "SYNOPSIS"
		print "\t%s [ --verbose | --help ]\n" % sys.argv[0]
		print "COMMAND LINE OPTIONS"
		print "\t--verbose : print verbose messages."
		print "\t--help: display this help and exit."
		sys.exit(0)
	else:
		print "\nUSE: %s [ --verbose | --help ]\n" % sys.argv[0]
		sys.exit(0)	
except IndexError:
	verbose = False

check_installed_python()

do_create_dirs_and_copy_files()

print "Testfarm was succesfully installed."
