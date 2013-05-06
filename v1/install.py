#! /usr/bin/python
import sys, os, shutil, glob, errno

verbose = True

PYTHON_NEEDED_VERSION = "python2.4"

def print_verbose(msg):
	if verbose: sys.stdout.write(msg+"\n") 
def error(msg):
	print "\nERROR: "+msg
	sys.exit(-1)

def check_installed_python():
	print_verbose("checking installed python version ... ")
	
	global python_version
	python_version = "python%s.%s" % ( sys.version_info[0], sys.version_info[1] )
	if python_version < PYTHON_NEEDED_VERSION :
		error("'%s' version was found, but Python 2.4 or greater is needed" % python_version)
	print_verbose("Python version found is Ok: %s" % python_version)
	return python_version

def do_create_dirs_and_copy_files( python_version ):
	print_verbose("checking operating system ... ")
	if sys.platform == 'win32' :
		print_verbose("Win32-like system\n")
		site_packages = "%s\lib\site-packages" % sys.prefix
		TESTFARM_DIR = "%s\\testfarm" % site_packages
	else :
		print_verbose("Unix-like system\n")
		site_packages = "%s/lib/%s/site-packages" % ( sys.prefix, python_version )
		TESTFARM_DIR = "%s/testfarm" % site_packages
	print_verbose("Creating tesfarm directory at %s ... " % TESTFARM_DIR)
	try:
		os.mkdir( TESTFARM_DIR ) # this command needs ROOT privileges
	except OSError, oserror:
		if errno.errorcode[oserror.errno] == 'EEXIST' :
			print_verbose("Dir already existed. That's ok.")
		else :
			error( "Cannot create dir %s. Are you root?\n" + oserror.strerror )
	print_verbose("Successfully created dir.\nCopying files...\n")
	try:
		filesToInstall = glob.glob("src/*.py")
		for file in filesToInstall :
			print_verbose('  installing: %s -> %s' % (file, TESTFARM_DIR) )
			shutil.copy('%s' % file, TESTFARM_DIR) # this command needs ROOT privileges
	except IOError, ioerror:
		error( "Cannot install files. Are you root?\n" + ioerror.strerror )
	print "Successfully installed %i files\n" % len(filesToInstall)
		

#  main :

python_version = check_installed_python()
do_create_dirs_and_copy_files( python_version )
print "testfarm was succesfully installed."
