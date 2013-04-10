#!/usr/bin/python

import subprocess
import sys
import os

def loadDictFile(dictfile) :
	""" Returns a dict with the variables defined in a file """
	class temp : exec(open(dictfile))
	loaded = dict(temp.__dict__)
	del loaded['__doc__']
	del loaded['__module__']
	return loaded

def die(message, exitCode=-1) :
	""" Exits the program by prompting a message using the do-this-or-die idiom. """
	print >> sys.stderr, "\033[31m%s\033[0m"%message
	sys.exit(exitCode)

def warning(message) :
	""" Outputs a warning message. """
	print >> sys.stderr, "\033[33m%s\033[0m"%message

def stage(message) :
	""" Outputs an stage message. """
	print >> sys.stderr, "\033[35m=== %s === \033[0m"%message

class tee :
	""" Output file decorator that duplicates the output to two files. """
	def __init__(self, file1, file2) :
		self.f1=file1
		self.f2=file2
	def flush(self):
		self.f1.flush()
		self.f2.flush()
	def write(self, content) :
		self.f1.write(content)
		self.f2.write(content)

class buffer :
	""" Output file decorator that memorizes the output so you can retrieve it later. """
	def __init__(self) :
		self._output = []
	def flush(self):
		pass
	def write(self, content) :
		self._output.append(content)
	def output(self) :
		return ''.join(self._output)

class quotedFile :
	""" Output file decorator that, surrounds the content of each write
	in between 'incode' and 'outcode'. """
	def __init__(self, aFile, incode, outcode) :
		self.incode = incode
		self.outcode = outcode
		self.f = aFile
	def write(self,content) :
		if not content : return
		self.f.write(self.incode)
		self.f.write(content)
		self.f.write(self.outcode)
	def flush(self):
		self.f.flush()

class ansi2html :
	def __init__(self, aFile) :
		self.f = aFile
		self._bold = False
		self._underline = False
		self._color = 1
	def write(self, content) :
		# todo filter content
		assert False, "Not implemented"
		self.f.write(content)

def run(command, message=None, log=sys.stdout, err=None, fatal=True, cwd=None) :
	if message is None : message = "Running: " + command
	if message :
		print "\033[32m== %s\033[0m"%(message)
	if err is None :
		err = quotedFile(log, "\033[31m", "\033[0m")
	# TODO: Exception save implementation of dir changing
	if cwd :
		oldcwd = os.getcwd()
		os.chdir(cwd)
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if cwd :
		os.chdir(oldcwd)
	import select
	outpoll = select.poll()
	outpoll.register(process.stdout.fileno())
	outpoll.register(process.stderr.fileno())
	while process.returncode is None :
		process.poll()
		for fd, flags in outpoll.poll() :
			if fd==process.stderr.fileno() :
				err.write(process.stderr.readline())
			if fd==process.stdout.fileno() :
				log.write(process.stdout.readline())
	log.write(process.stdout.read())
	err.write(process.stderr.read())
	if fatal and process.returncode : die("Failed, exit code %i"%process.returncode, process.returncode)
	return process.returncode == 0

def output(command, message=None, fatal=True) :
	print "\033[32m== Output of: %s\033[0m"%(message or command)
	proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	output = proc.communicate()[0]
	if fatal and proc.returncode : die("Failed, exit code %i"%proc.returncode, proc.returncode)
	return output

def hasOption(option) :
	if option not in sys.argv :
		return False
	sys.argv.remove(option)
	return True

def parameterOption(option) :
	if option not in sys.argv :
		return None
	optionIndex = sys.argv.index(option)
	value = sys.argv[optionIndex+1]
	del sys.argv[optionIndex:optionIndex+2]
	return value

