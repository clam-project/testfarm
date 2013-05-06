#!/usr/bin/python
import sys
if len(sys.argv) < 3 :
	print """
This script launches a commandline just if it can adquire a given lock
file. It can be used to avoid duplicated instances of an application.
$ runOnce.py /path/to/the/lock/file.lock program arg1 arg2....
"""
	sys.exit(-1)

import os

class FileLock :
	def __init__(self, filename) :
		try:
			self.filename = filename
			self.lockfd = os.open(filename, os.O_RDWR|os.O_EXCL|os.O_CREAT)
			os.write(self.lockfd, str(os.getpid()))
		except OSError:
			self.lockfd = None
	def wasAdquired(self): return not self.lockfd is None
	def __del__(self) :
		if not self.lockfd : return
		os.close(self.lockfd)
		os.remove(self.filename)

import time
import sys
import subprocess
lockfile = sys.argv[1]
command = sys.argv[2:]
lock = FileLock(lockfile)
if lock.wasAdquired() :
	subprocess.call(command)
	del lock
	sys.exit()

print "Already running. Remove the file %s if you think it is not"%lockfile

