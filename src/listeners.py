#
#  Copyright (c) 2006 Pau Arumi, Bram de Jong, Mohamed Sordo 
#  and Universitat Pompeu Fabra
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#

import sys


class MultiListener(object) :
	"Forwards method calls to a set of added objects"

	class wrapper(object) :
		def __init__(self, wrapped, method) :
			self.wrapped = wrapped
			self.method = method
		def __call__(self, *args, **keyw) :
			self.wrapped._multicall(self.method, *args, **keyw)

	def __init__(self, subs=[]) :
		self._added = subs[:]

	def add(self, sub) :
		self._added.append(sub)

	def __getattr__(self, method ) :
		"Whenever you access an non-existing attribute or method"
		return MultiListener.wrapper(self, method)

	def _multicall(self, method, *args, **keyw) :
		"Not to be called directly"
		return [ 
			getattr(sub,method) (*args, **keyw)
			for sub in self._added
		]


class NullResultListener : #TODO base class
	"Discards messages"
	def listen_end_command(self, command, ok, output, info, stats):
		pass
	def listen_begin_command(self, cmd):
		pass
#	def listen_end_command(self, cmd):
#		pass
	def listen_begin_subtask(self, subtaskname):
		pass	
	def listen_end_subtask(self, subtaskname):
		pass	
	def listen_begin_task(self, taskname):
		pass
	def listen_end_task(self, taskname, status):
		pass
	def listen_task_info(self, task):
		pass
	def listen_found_new_commits( self, new_commits_found, seconds_idle ):
		pass
	def listen_end_task_gently(self, taskname):
		pass 

class DummyResultListener(NullResultListener) :
	"helper ResultListener class "
	def __init__(self):
		self.results = []

	def log(self) :
		return "\n".join( self.results )

	def listen_end_command(self, command, ok, output, info, stats):
		if ok :
			status_text = "ok"
		else :
			status_text = "failure"
		self.results.append( str( (command, status_text, output, info, stats) ) )

	def listen_begin_command(self, cmd):
		#self.results.append("BEGIN_CMD %s" % cmd)
		pass
	
#	def listen_end_command(self, cmd):
#		self.results.append("END_CMD %s" % cmd)

	def listen_begin_subtask(self, subtaskname):
		self.results.append( "BEGIN_SUBTASK %s" % subtaskname )

	def listen_end_subtask(self, subtaskname):
		self.results.append( "END_SUBTASK %s" % subtaskname )
	
	def listen_begin_task(self, taskname):
		self.results.append( "BEGIN_TASK %s" % taskname )

	def listen_end_task(self, taskname, status):
		self.results.append( "END_TASK %s" % taskname )
	
	def listen_found_new_commits( self, new_commits_found, seconds_idle ):
		pass
	def listen_end_task_gently(self, taskname):
		pass 

class ConsoleResultListener(NullResultListener) :
	"Prints execution status and progress in console mode."
	def __init__(self):
		self.results = []

		self.colors = {
			'BOLD'  :"\x1b[01m",
			'RED'   :"\x1b[31;01m",
			'GREEN' :"\x1b[32;01m",
			'YELLOW':"\x1b[33;01m", # unreadable on white backgrounds
			#'YELLOW':"\033[1m", #"\033[93m" # unreadable on white backgrounds
			'CYAN'  :"\x1b[36;01m",
			'MAGENTA':"\x1b[35;01m", 
			'NORMAL':"\x1b[0m",
			}
			
	def color(self, name):
		if sys.platform == 'win32':
			return ""
	
		try:
			return self.colors[name]
		except:
			return ""

	def pprint(self, col, str, label=''):
		mycol = self.color(col)
		print "%s%s%s %s" % (mycol, str, self.color('NORMAL'), label)

	def pprint_cmd_result(self, cmd, status_ok, output, info, stats):
		normal = self.color('NORMAL')
		yellow = self.color('YELLOW')
		red = self.color('RED')
		green = self.color('GREEN')
		if status_ok:
			status_text = green+'[ ok ]'+normal
		else :
			status_text = red+'[ failure ]'+normal
		if output :
			ending = '%s---------------------------------------------\n' % yellow
			ending += 'Output of failing command:%s\n\n%s\n' % (normal, output)
			ending += '\n%s---------------------------------------------%s\n' % (yellow, normal)
		else:
			ending = ''
		sys.stdout.write("\n".join([
			"\t\t%s"%(status_text),
			"    | %sinfo:%s %s"%(yellow, normal, info),
			"    | %sstats:%s %s"%(yellow, normal, stats),
			"%s    |"% (ending),
			]))

	def pprint_begin_cmd(self, cmd):
		cmd_color = self.color('CYAN')
		yellow = self.color('YELLOW')
		normal = self.color('NORMAL')
		sys.stdout.write( "    + %scmd:%s%60s%s" % (yellow, cmd_color, cmd, normal) )
		sys.stdout.flush()
	
	def listen_end_command(self, cmd, ok, output, info, stats):
		self.pprint_cmd_result( cmd, ok, output, info, stats )

	def listen_begin_command(self, cmd):
	#	self.pprint('BOLD', "    BEGIN_CMD %s" % cmd )
		self.pprint_begin_cmd(cmd)	
	
#	def listen_end_command(self, cmd):
#		self.pprint ('BOLD', "    END_CMD %s\n" % cmd )
	
	def listen_begin_subtask(self, subtaskname):
		self.pprint('BOLD', "  BEGIN_SUBTASK %s" % subtaskname )

	def listen_end_subtask(self, subtaskname):
		self.pprint('BOLD', "  END_SUBTASK %s\n" % subtaskname )
	
	def listen_begin_task(self, taskname):
		self.pprint('BOLD', "BEGIN_TASK %s\n" % taskname )

	def listen_end_task(self, taskname, status):
		self.pprint('BOLD', "END_TASK %s --> %s" % (taskname, status) )

	def listen_found_new_commits( self, new_commits_found, seconds_idle ):
		self.pprint('MAGENTA', 'New commits found, or No checks specified :', new_commits_found)
		self.pprint('MAGENTA', 'New check in %d seconds.' % seconds_idle)

	def listen_end_task_gently(self, taskname):
		self.pprint('MAGENTA', 'Keyboard Interrupt. Stopping execution gently') 

