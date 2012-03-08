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

"""
TODO
* separate html formatting code in a different class/source file
* Server should become a LogsFormatter something that on construction
  takes the filesystem logs state and writes html. But should not persist 
  in memory (as now remote_server_timer does)
* clients glob should be done only once (at constructor)
* do not use a huge testfarmlog file, but a different log file for each execution
  easier to clean old history
* regenerate only the necessary. 
 

"""

import datetime, os, glob, sys
import subprocess
from dirhelpers import *

header_index = """\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<meta http-equiv="refresh" content="120">
<link href="style.css" rel="stylesheet" type="text/css">
<title>Tests Farm for project %(project_name)s </title>
<script type="text/javascript" language="JavaScript1.2" src="testfarm_info.js"></script>
<script language="JavaScript1.2">
document.onmousedown=ddInit;
document.onclick=hideMe();
</script>
</head>
<body>
<div id="theLayer" class="layer"></div>
<h1>testfarm for project <a>%(project_name)s
<span class='tooltip'>%(project_info)s</span></a>
<span class='description'>%(project_brief_description)s</span>
</h1>

"""

header_details = """\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<link href="style.css" rel="stylesheet" type="text/css">
<title>Tests Farm Details</title>
<script type="text/javascript" language="JavaScript" src="testfarm.js"></script>
</head>
<body>
"""

footer = """
<div class="about">
<p>TestFarm is free software. Learn <a href="http://testfarm.sf.net/">about TestFarm</a>.</p>
</div>
</body>
</html>
"""

def ansiterminal2Html(text, tabstop=4) :
	import re
	import cgi

	colorcodes =   {
		'bold':{True:'\033[1m',False:'\033[0m'},
		'red':{True:'\033[31m',False:'\033[0m'},
		'green':{True:'\033[32m',False:'\033[0m'},
		'#444400':{True:'\033[33m',False:'\033[0m'},
		'blue':{True:'\033[34m',False:'\033[0m'},
		'magenta':{True:'\033[35m',False:'\033[0m'},
		'cyan':{True:'\033[36m',False:'\033[0m'},
		'underline':{True:'\033[4m',False:'\033[0m'},
		'lightgreen':{True:'\033[32;1m',False:'\033[0m'},
		'#ff7777':{True:'\033[31;1m',False:'\033[0m'},
		}

	def recolor(color, text):
		regexp = "(?:%s)(.*?)(?:%s)" % (colorcodes[color][True], colorcodes[color][False])
		regexp = regexp.replace('[', r'\[')
		return re.sub(regexp, r'''<span style="color: %s; font-weight:bold;">\1</span>''' % color, text)

	def bold(text):
		regexp = "(?:%s)(.*?)(?:%s)" % (colorcodes['bold'][True], colorcodes['bold'][False])
		regexp = regexp.replace('[', r'\[')
		return re.sub(regexp, r'<span style="font-weight:bold">\1</span>', text)

	def underline(text):
		regexp = "(?:%s)(.*?)(?:%s)" % (colorcodes['underline'][True], colorcodes['underline'][False])
		regexp = regexp.replace('[', r'\[')
		return re.sub(regexp, r'<span style="text-decoration: underline">\1</span>', text)

	def removebells(text):
		return text.replace('\07', '')

	def removebackspaces(text):
		backspace_or_eol = r'(.\010)|(\033\[K)'
		n = 1
		while n > 0:
			text, n = re.subn(backspace_or_eol, '', text, 1)
		return text
	re_string = re.compile(r'(?P<htmlchars>[<&>])|(?P<space>^[ \t]+)|(?P<lineend>\r\n|\r|\n)|(?P<protocal>(^|\s)((http|ftp)://.*?))(\s|$)', re.S|re.M|re.I)
	def do_sub(m):
		c = m.groupdict()
		if c['htmlchars']:
			return cgi.escape(c['htmlchars'])
		if c['lineend']:
			return '<br>'
		elif c['space']:
			t = m.group().replace('\t', '&nbsp;'*tabstop)
			t = t.replace(' ', '&nbsp;')
			return t
		elif c['space'] == '\t':
			return ' '*tabstop;
		else:
			url = m.group('protocal')
			if url.startswith(' '):
				prefix = ' '
				url = url[1:]
			else:
				prefix = ''
			last = m.groups()[-1]
			if last in ['\n', '\r', '\r\n']:
				last = '<br>'
			return '%s%s' % (prefix, url)
#	result = re.sub(re_string, do_sub, text)
	result = text
	result = bold(result)
	result = underline(result)
	result = removebells(result)
	result = removebackspaces(result)
	for color in colorcodes :
		result = recolor(color, result)
	print result
	return result



		

#
#     SERVER
#
class Server:
	"Reads the logs from a directory defined by the project name, structures the data and prints it as HTML pages"
	def __init__(self, 
		logs_base_dir = '/tmp/testfarm_tests',
		html_base_dir = '/tmp/testfarm_html',
		project_name = None,
	) :
		self.logs_base_dir = logs_base_dir 
		self.html_base_dir = html_base_dir
		create_dir_if_needed( html_base_dir )
		if project_name: #TODO not very sure of this  (PA)
			create_dir_if_needed( '%s/%s' % (html_base_dir, project_name) )
			self.project_name = project_name
		else:
			print 'Warning: html dir was not created because Server was not initialized with a project_name'


	def log_path(self, filename) :
		"Builds a path name for a log file for the current project"
		return os.path.join(
			self.logs_base_dir,
			self.project_name,
			filename)

	def client_log_path(self, client) :
		return self.log_path("%s.testfarmlog"%client)

	def client_idle_path(self, client) :
		return self.log_path("%s.idle"%client)

	def client_info_path(self, client) :
		return self.log_path("%s.info"%client)

	def project_info_path(self) :
		return self.log_path("%s.info"%self.project_name)

	def load_tuples(self, filename) :
		print "Loading '%s'..."%filename
		try :
			return eval("[ %s ]" % open( filename ).read() )
		except IOError:
			return None

	def load_dict(self, filename) :
		print "Loading '%s'..."%filename
		try :
			content = open( filename ).read() 
		except IOError:
			return {}
		if not content :
			return {}
		return eval( content )


	def web_path(self, filename) :
		"Builds a path name for a html output for the current project"
		return os.path.join(
			self.html_base_dir,
			self.project_name,
			filename)

	def web_write(self, filename, content) :
		fullpath = self.web_path(filename)
		print "Generating '%s'..." % fullpath
		f = open( fullpath, 'w' )
		f.write( content )
		f.close()
		return fullpath


	def clients_sorted(self):
		"Returns all client's names in the project"

		assert self.project_name, "Error, project_name was expected. But was None"
		logfiles = glob.glob(self.client_log_path('*'))
		result = map( remove_path_and_extension, logfiles)
		result.sort()
		return result

	def load_client_log(self, client_name):
		filename = self.client_log_path(client_name)
		return self.load_tuples(filename)

	def load_client_idle(self, client_name):
		filename = self.client_idle_path(client_name)
		return self.load_dict(filename)

	def load_client_info(self, client_name):
		filename = self.client_info_path(client_name)
		return self.load_tuples(filename)

	def load_project_info(self):
		filename = self.project_info_path()
		return self.load_tuples(filename)
	
	def last_date(self, log):
		"Returns the date of the last task executed given a logfile"
		log.reverse()
		for entry in log :
			tag = entry[0]
			if tag == 'BEGIN_TASK':
				return entry[2]
		assert "BEGIN_TASK not found"

	def single_execution_details(self, client_name, wanted_date):
		"Retrieves a single execution from a logfile given the date of the execution"
		log = self.load_client_log(client_name)
		result = []
		in_wanted_execution = False
		for entry in log :
			tag = entry[0]
			if not in_wanted_execution :
				if tag == 'BEGIN_TASK' and entry[2] == wanted_date :
					in_wanted_execution = True
			if in_wanted_execution :
				result.append(entry)
				if tag == 'END_TASK' :
					in_wanted_execution = False
					break
		return result

	def purge_client_logfile(self, client_name, last_date):
		"Deletes (large) INFO and OUTPUT entries from logfile"
		log = self.load_client_log(client_name)
		date = ''
		logfilename = self.client_log_path(client_name )
		updated_log = []
		for entry in log :
			tag = entry[0]
			count = 0
			if tag == 'BEGIN_TASK':
				#assert entry[2] != date, "Error. found two repos with same date."
				#TODO fix
				if entry[2] == date : print "Warning", "Error. found two repos with same date."
				date = entry[2]
				count = 1
				updated_log.append('\n')

			# write the maybe modified entry in an auxiliar file
			if tag == 'END_CMD' and date != last_date:
				postfix = '%s_%s_%s' % (client_name, date, count)
				new_entry = self.__extract_info_and_output_to_auxiliar_file(entry, postfix)
				updated_log.append( '%s,\n' % str(new_entry) )
				count += 1
			else :
				updated_log.append( '%s,\n' % str(entry) )
		#TODO writing the log files is potentially  dangerous !! (if somebody else is reading at the moment)
		#     actually, another client might be reading it through the serverproxy / server_side_logger
		#     a solution seems to be blocking the file access
		f = open(logfilename, 'w') 	
		f.writelines( updated_log )
		f.close()
				
	def __extract_info_and_output_to_auxiliar_file( self, cmd_tuple, postfix ):
		"Moves INFO and OUTPUT entries to separated files"
		extracted_note = '[SAVED TO FILE]'
		output = cmd_tuple[3]
		info = cmd_tuple[4]
		if output and output != extracted_note :
			filename = self.log_path('purged_output__%s' %postfix)
			f = open(filename, 'w')
			f.write(output)
			f.close()
			output = extracted_note
		else:
			pass
		#	print 'dont extract output: ', output

		if False and info and info != extracted_note : #DISABLED for efficiency - Pau
			filename = self.log_path('purged_info__%s' %postfix)
			f = open(filename, 'w')
			f.write( str(info) ) #non string can be passed as info. so str() is needed 
			f.close()
			info = extracted_note
		else:
			pass
		#	print 'dont extract output: ', output
		return (
			cmd_tuple[0], # tag END_CMD 
			cmd_tuple[1], # "the" cmd
			cmd_tuple[2], # status
			output,
			info,
			cmd_tuple[5] # stats
			)	

	def __html_single_execution_details(self, client_name, wanted_date):
		"Creates an HTML file with the details of an execution given a date"
		class Namespace() : pass
		f=Namespace() # so that inner functions can modify the following vars
		f.content = []
		f.id_info = 1
		f.id_output = 1
		f.opened_task = False
		f.opened_subtask = False
		f.opened_cmd = False

		def BEGIN_TASK(taskname, begin_date) :
			#assert not f.opened_task
			#assert not f.opened_subtask
			#assert not f.opened_cmd
			f.content.append('<div class="task"> BEGIN_TASK "%s" %s' % (taskname, begin_date) )
			f.opened_task = True
		def BEGIN_SUBTASK(subtaskname) :
			#assert f.opened_task
			#assert not f.opened_subtask
			#assert not f.opened_cmd
			subtask_name = entry[1]
			f.content.append('<div class="subtask"> BEGIN_SUBTASK "%s"' % subtaskname )
			f.opened_subtask = True
		def BEGIN_CMD(command) :
			#assert f.opened_task
			#assert f.opened_subtask
			#assert not f.opened_cmd
			f.content.append( '<div class=command>' )
			f.content.append( '<span class="command_string"> %s</span>' % command )
			f.opened_cmd = True						
		def END_SUBTASK(subtask_name) :
			#assert f.opened_task
			#assert f.opened_subtask
			#assert not f.opened_cmd
			f.content.append('END_SUBTASK "%s"</div>' % subtask_name)
			f.opened_subtask = False
		def END_TASK(task_name, end_time, status) :
			if f.opened_cmd:
				#assert f.opened_task
				#assert f.opened_subtask
				f.content.append( '<span class="command_failure">[FAILURE]</span>' )
				f.content.append( '<p class="output"> command execution aborted by the client</p>')
				f.content.append('</div>')
			if f.opened_subtask:
				#assert f.opened_task
				f.content.append('</div>')
			f.content.append( 'END_TASK "%s" %s %s</div>' % (task_name, end_time, status) )
			#exiting, so no need to make f.opened_task=False
			return header_details + '\n'.join(f.content) + footer	
		def END_CMD(command, ok, output, info, stats) :
			#assert f.opened_task
			#assert f.opened_subtask
			#assert f.opened_cmd
			if ok :
				f.content.append( '<span class="command_ok">[OK]</span>' )
			else:
				f.content.append( '<span class="command_failure">[FAILURE]</span>' )
				f.content.append( '<p id="output%d" class="output"> OUTPUT:<br /> %s </p>' % ( f.id_output, ansiterminal2Html(output) ) )
				if output.count('\n') > 5 :
						f.content.append( ' <script type="text/javascript">togglesize(\'output%d\');</script> ' % f.id_output )
				f.id_output += 1
			if info :
				f.content.append( '<p id="info%d" class="info"> INFO:<br />%s </p>' % ( f.id_info, ansiterminal2Html(info) ) )
				if info.count('\n') > 5 :
						f.content.append( ' <script type="text/javascript">togglesize(\'info%d\');</script> ' % f.id_info )
				f.id_info += 1
			if stats :
				f.content.append(  '<p class="stats"> STATS: {%s} </p>' % ''.join(stats) )
			f.content.append( '</div>' )
			f.opened_cmd = False

		for entry in self.single_execution_details(client_name, wanted_date ):
			tag = entry[0].strip()
			assert tag in [
				'BEGIN_TASK',
				'END_TASK',
				'BEGIN_SUBTASK',
				'END_SUBTASK',
				'BEGIN_CMD',
				'END_CMD',
				], 'Log Parsing Error. Bad entry tag: "%s"' % tag
			locals()[tag](*entry[1:])

		if f.opened_cmd :
			f.content.append( '<span class="command_inprogress">in progress ...</span>' )
			f.content.append( '</div>')
		if f.opened_subtask :
			f.content.append( '</div>')
		if f.opened_task :	
			f.content.append( '</div>')
			
		return header_details + '\n'.join(f.content) + footer	

	#minimal version:
#	def html_single_execution_details(self, client_name, wanted_date):
#		content = ["<pre>"]
#		for entry in self.single_execution_details(client_name, wanted_date ):
#			content.append( "\n".join( map(str, entry) ) )	
#		content.append("</pre>")
#		return header_details + "\n".join(content) + footer

	def __write_details_static_html_file(self, client_name, wanted_date):
		"Writes an HTML file with the details of an execution given a date"
		details = self.__html_single_execution_details(client_name, wanted_date)
		filename = "details-%s-%s.html" % ( client_name, wanted_date )
		return self.web_write(filename, details)
	
	def __get_client_executions(self, client_name): #TODO: MS - Refactor
		"Returns all task executions given a client name"
		log = self.load_client_log(client_name)
		executions = []
		execution_opened = False
		begin_time = ''
		for entry in  log :
			tag = entry[0]
			if tag == 'BEGIN_TASK' :
				repo_name = entry[1]
				begin_time = entry[2]
				execution_opened = True
			if tag == 'END_TASK' :
				end_time = entry[2]
				status_ok = entry[3]
				if status_ok == 'True' : #TODO change to "Success"
					status = 'stable'
				elif execution_opened and status_ok == 'Aborted' :
					status = 'aborted'
				else :
					status = 'broken'
				if not begin_time:
					print "Warning: Error in log file. Non matching END_TASK. client:" + client_name
					continue
				executions.append( (begin_time, end_time, repo_name, status) )
				execution_opened = False
		if execution_opened :
			assert begin_time, "Error in log file. End of log without any BEGIN_TASK"
			executions.append( (begin_time, '', repo_name, 'inprogress') )
		executions.reverse()
		return executions

	def __collect_client_stats(self, client_name):
		"Collect all client's stats entries from client's logfile"
		log = self.load_client_log(client_name)
		allstats = {}
		begin_time = ''
		for entry in log :
			tag = entry[0]
			if tag == 'BEGIN_TASK':
				begin_time = entry[2]
			elif tag == 'BEGIN_SUBTASK':
				if not begin_time : # "found BEGIN_SUBTASK before BEGIN_TASK"
					continue
				current_task = entry[1]
			elif tag == 'END_CMD' :
				if not begin_time: # "found END_CMD before BEGIN_TASK"
					continue
				stats_entry = entry[5]
				if not stats_entry:
					continue
				assert current_task, "Error: found statistics (STATS) stats in an unamed task"
				if not allstats.has_key(current_task) :
					allstats[current_task] = []
				allstats[current_task].append( (begin_time, stats_entry) )
		return allstats

	def __get_missing_details_dates(self, log, client_name):
		"Returns dates of all task executions in logfile that haven't a details HTML file"
		log.reverse()
		missing_details_dates = []
		begin_task_found = False
		for entry in log :
			tag = entry[0]
			if tag != 'BEGIN_TASK': continue
			begin_date = entry[2]
			begin_task_found = True
			details_filename = self.web_path("details-%s-%s.html"%(client_name, begin_date))
			if not os.path.isfile(details_filename):
				missing_details_dates.append(begin_date)	
			else:
				break
	# TODO: why this assert? prevents starting without log files
	#	assert begin_task_found, "BEGIN_TASK not found" 
		return missing_details_dates
	

	def write_missing_details_static_html(self):
		"Writes details HTML file for those task executions without it"
		filenames = []
		for client in self.clients_sorted():
			client_log = self.load_client_log(client)
			missing_dates = self.__get_missing_details_dates(client_log, client)
			for missing_date in missing_dates :
				filename = self.__write_details_static_html_file(client, missing_date)
				#purgue_client is still experimental:
 				self.purge_client_logfile(client, missing_date) #TODO improve purgue method
				filenames.append(filename)
		return filenames
	

	def idle(self):
		"Returns idle entries for all clients"
		result = {}
		for client_name in self.clients_sorted():
			idle_entry = self.load_client_idle(client_name)
			result[client_name] = idle_entry
		return result

	def get_executions(self):
		"Returns all client's task executions"
		result = {}
		for client_name in self.clients_sorted():
			result[client_name] = self.__get_client_executions(client_name)
		return result

	def __html_format_client_executions(self, client_name, client_idle, client_executions):
		"Generates HTML code for a client's task executions"
		content = []
		time_tmpl = "%(hour)s:%(min)s:%(sec)s %(D)s/%(M)s"
		if client_idle and not client_idle['new_commits_found'] :
			idlechecktime_str = client_idle['date']
			content_dict = {}
			content_dict['date'] = "<p>Last check done at : %s" % self.__format_datetime(
				idlechecktime_str, time_tmpl )
			content_dict['next_run_in_seconds'] = client_idle['next_run_in_seconds']
			content.append('''\
<div class="idle">
%(date)s
<p>Next check will be in %(next_run_in_seconds)s seconds </p>
</div>''' % content_dict)
		for begintime_str, endtime_str, task_name, status in client_executions:
			name_html = "<p>%s</p>" % task_name + " - " + client_name
			begintime_html = "<p>Begin time: %s </p>" % self.__format_datetime(begintime_str, time_tmpl)
			if not endtime_str :					
				endtime_html = "<p>in progres...</p>"
				actual_status = "in progress"
			elif status == "aborted" :
				endtime_html = "\n<p>Client Aborted: %s</p>" % self.__format_datetime(endtime_str, time_tmpl)
				actual_status = status
			else:
				endtime_html = "<p>End time: %s </p>" % self.__format_datetime(endtime_str, time_tmpl)
				actual_status = status
			details_filename = 'details-%s-%s.html' % (client_name, begintime_str)
			details_html = '<p><a href="javascript:details_info(\'%s\',\'%s\')">info</a> | <a href="%s">execution log</a></p>' % (actual_status, details_filename, details_filename)
			content.append( '<div class="%s">\n%s\n%s\n%s\n%s\n</div>' % (
				status, name_html, begintime_html, endtime_html, details_html) )
		return content

	"""def __initialize_clients_in_day_executions(self, day_executions, executions_per_client): #TODO: rename method
		# we have to initialize all clients in a day even though they are not present in it 
		for day in day_executions :
			day_clients = day_executions[day]
			for client in executions_per_client.keys():
				if client not in day_clients:
					day_clients[client] = []	
		return day_executions
	"""

	def day_executions(self, executions_per_client):
		"Returns client's task executions ordered by day"
		day_executions = {}
		# order executions per day
		time_tmpl = "%(Y)s-%(M)s-%(D)s"
		for client in executions_per_client.keys():
			client_executions = executions_per_client[client]
			for begintime_str, endtime_str, repo_name, status in client_executions:
				day = self.__format_datetime(begintime_str, time_tmpl)
				if day not in day_executions:
					day_executions[day] = {}
				if client not in day_executions[day]:
					day_executions[day][client] = []
		#		day_executions = self.__initialize_clients_in_day_executions(day_executions, executions_per_client)
				day_executions[day][client].append( (begintime_str, endtime_str, repo_name, status) )
		
		return day_executions

	def __executed_subtasks(self, client_name, execution_date) :
		return [
			entry[1]
			for entry in self.single_execution_details(client_name, execution_date )
			if entry[0] == 'BEGIN_SUBTASK'
			]
	def __failed_subtasks(self, client_name, execution_date) :
		failed_tasks = []
		current_task = None
		for entry in self.single_execution_details(client_name, execution_date ) :
			tag = entry[0]
			if tag == 'BEGIN_SUBTASK' :
				current_task, = entry[1:]
			if tag == 'END_CMD' :
				command, ok, output, info, stats = entry[1:]
				if ok : continue
				if not current_task : 'ERROR DETERMINING TASK'
				if current_task in failed_tasks : continue
				failed_tasks.append(current_task)
		return failed_tasks

	def __html_format_clients_day_executions(self, idle_per_client, executions_per_day, clients): # TODO : MS Finish Implementation
		"Generates HTML code for a client's task executions ordered by day"
		content = []
		# clients = self.clients_sorted() DOES NOT WORK PROPERLY
		executions_per_day_key_sorted = executions_per_day.keys()
		executions_per_day_key_sorted.sort(reverse = True)
		html_time_tmpl = "%(D)s/%(M)s/%(Y)s"
		is_last_day = True
		for day in executions_per_day_key_sorted :
			#content.append('<tr>')
			formatted_day = self.__format_datetime(day+'-00-00-00', html_time_tmpl)
			# this inserts a break line in the table indicating the day
			content.append('<tr><td colspan="%s" align="center">%s</td></tr><tr>' % (len(clients), formatted_day)) 
			day_clients = executions_per_day[day]
			for client in clients:
			#	print "CLIENT_KEY IN DAY CLIENTS = ", client
				content.append('<td>')
				client_executions = day_clients.get(client, []) # if client then return client executions , else return empty list
			#	print "CLIENT_VALUE IN DAY CLIENTS = ", client_executions
				if is_last_day :
					client_idle = idle_per_client[client]
				else : 	
					client_idle = {}
				content += self.__html_format_client_executions(client, client_idle, client_executions) 
				content.append('</td>')
			content.append('</tr>')
			is_last_day = False
		return content

	def __description_info_to_html(self, info_tuples) :
		project_info = ""
		brief_description = " "

		if not info_tuples : return '', ''
		
		for entry in info_tuples :
			name, value = entry[:2]
			if name == "Brief description" :
				brief_description = value
			if name == "Long description" :
				project_info = value
		return project_info, brief_description
		

	def __html_project_info(self):
		"Generates HTML code for the project information file"
		return self.__description_info_to_html(self.load_project_info())

	def __html_client_info(self, client_name): #TODO : remove code duplication
		"Generates HTML code for the client information file"
		return self.__description_info_to_html(self.load_client_info(client_name))

	def __json_data(self, clients_with_stats):
		"Creates the js data for the project"
		project_info, project_brief_description = self.__html_project_info()
		executions_per_client = self.get_executions()
		idle_per_client = self.idle()
		def format_date(date) :
			return date.strftime("%Y/%m/%d %H:%M:%S")
		content = [
			'{',
			'	"project": "%s",' % self.project_name,
			'	"lastupdate": "%s",'%format_date(datetime.datetime.now()),
			'	"clients":',
			'	[',
			]
		for client in self.clients_sorted() :
			client_info, client_brief_description = self.__html_client_info(client)
			executions = sorted(executions_per_client[client])
			if not executions: continue
			idle_info = idle_per_client[client]
			print "new_commits_found:", idle_info['new_commits_found']
			current_task = None
			for start, stop, name, status in reversed(executions) :
				if status != 'inprogress' : break # found a finished task
				if current_task : continue # already have an inprogress task
				subtasks = self.__executed_subtasks(client, start)
				current_task = "Step %i: %s"%(len(subtasks),subtasks[-1]) if subtasks else "Starting up execution"

			status_map = {
				'broken': 'red',
				'stable': 'green',
				'aborted': 'int',
				'inprogress': 'int', # TODO: considering single inprogress execution
				}
			last_update = datetime.datetime(*[int(a) for a in idle_info['date'].split('-')])
			next_update = last_update + datetime.timedelta(seconds = idle_info['next_run_in_seconds'])
			failed_tasks = self.__failed_subtasks(client, start)

			doing = "run" if current_task else (
				"old" if next_update < datetime.datetime.now() else
				"wait"
				)
			content += [
				'		{',
				'			"name": "%s",' % client,
				'			"description": %s,' % repr(client_info),
				'			"name_details": \'%s\',' % client_brief_description,
				'			"status": "%s",'% status_map[status],
				'			"doing": "%s",' % doing,
				'			"lastupdate": "%s",' % format_date(last_update),
				] + ([
				'			"failedTasks":',
				'			[',
				] + [
				'				"%s",' % task
					for task in failed_tasks # todo
				] + [
				'			],',
				] if failed_tasks else []) + ([
				'			"currentTask": "%s",' % current_task,
				] if current_task else []) + [
				'		},',
				]
		content += [
			'	]',
			'}',
		]
		return "\n".join(content)

	def __html_index(self, clients_with_stats):
		"Creates the main HTML file for the project"
		project_info, project_brief_description = self.__html_project_info()
		executions_per_client = self.get_executions()
		idle_per_client = self.idle()
		content = ['<table>']

		# Client descriptions
		content.append('<tr>')
		for client in self.clients_sorted() :
			client_info, client_brief_description = self.__html_client_info(client)
			content.append(
				"<th> Client: <a>%s"
				"<span class='tooltip'>%s</span></a>"
				"<p width=\"100%%\">%s</p></th> " % (
					client,
					client_info,
					client_brief_description,
				))
		content.append('</tr>')

		# Stats
		content.append('<tr>')
		for client in self.clients_sorted():
			if client in clients_with_stats:
				thumb_html = '<a href="%s-stats.html"><img src="%s_1-thumb.png" /></a> <a href="%s-stats.html">more...</a>' % (client, client, client)
			else:
				thumb_html = ''
			content.append('<td style="text-align:center"> %s </td>' % thumb_html)
		content.append('</tr>')	

		executions_per_day = self.day_executions(executions_per_client)
		content += self.__html_format_clients_day_executions(idle_per_client, executions_per_day, self.clients_sorted() )
		content.append('</table>')
		return header_index % {
					'project_name':self.project_name+":", 
					'project_info':project_info,
					'project_brief_description':project_brief_description
					} + '\n'.join(content) + footer
		
	def __helper_apache_log(self, msg):
		'debugging method'
		from mod_python import apache
		apache.log_error('TestFarm:  '+ str(msg) )
		
	def update_static_html_files(self):
		"Updates all project's HTML files"
		newfiles, clients_with_stats = self.plot_stats()
		for client in self.clients_sorted():
			print 'Processing project %s, client %s'% (self.project_name, client)
			client_log = self.load_client_log(client)
			last_date = self.last_date(client_log)
			filename = self.__write_details_static_html_file(client, last_date)
			#purgue_client is still experimental:
 			self.purge_client_logfile(client, last_date) #TODO improve purgue method
			
			newfiles.append(filename)
		newfiles.append(self.web_write('index.html', self.__html_index(clients_with_stats)))
		newfiles.append(self.web_write('testfarm-data.js', self.__json_data(clients_with_stats)))

	def collect_stats(self):
		"Collect statistics for all clients"
		result = {}
		for client in self.clients_sorted():
			result[client] = self.__collect_client_stats(client)
		return result

	def __assert_all_keys_equal_length(self, stats, length):
		keys = stats.keys()
		for key in keys:
			assert length == len(stats[key]), "Error found stat with diferent length. key: %s\n%s" %(key, stats)

	def __format_datetime(self, time_str, pattern, time_tags = ["Y", "M", "D", "hour", "min", "sec"]) :
		"Gives format for a date time"
		time_dict = dict(zip( time_tags, time_str.split("-") ))
		return pattern % time_dict 

	def plot_stats(self): # TODO refactor extract methods
		"Plots all statistics"
		allclients_stats = self.collect_stats()
		clients = allclients_stats.keys()
		clients_with_stats = []
		images = []
		pngs = []
		pngs_thumb = []
		svgs = []
		for client in clients:
			diagram_count = 0
			alltasks_stats = allclients_stats[ client ]	
			for task in alltasks_stats.keys():
				stats_list = alltasks_stats[task ]
				if stats_list :
					clients_with_stats.append( client )
				else:
					continue

				diagram_count += 1

					
				# 1. collect all keys and remove spaces
				allkeys = set()
				for time, stat in stats_list:
					allkeys.update( stat.keys() )
				normalizedkeys = map(lambda x: '_'.join(x.split()), allkeys) #TODO this lambda should be global function

				# 2. write a line for each item in a list
				diagram_name = '%s_%d' % (client, diagram_count)
				plotfilename = self.log_path('%s.plot' % diagram_name)

				plotfile_content = ['time']
				for key in normalizedkeys :
					plotfile_content.append( '\t'+key )
				plotfile_content.append('\n')

				for time, stat in stats_list:
					plotfile_content.append( self.__format_datetime(time, "%(Y)s/%(M)s/%(D)s.%(hour)s:%(min)s") )
					for key in allkeys: 
						plotfile_content.append( '\t'+str( stat.get(key, '-') ) )
					plotfile_content.append('\n')

				# 3. write list to file
				f = open(plotfilename, 'w')
				f.writelines( plotfile_content )
				f.close()

				# 4. execute ploticus command
				columns = ""
				for i in range(len(allkeys)-1): # "y=1" already in the ploticus_cmd
					columns += " y%d=%d" % (i+2, i+3) # y2=3 y3=4, etc.

				png_filename = self.web_path('%s.png' % diagram_name)
				png_thumbfilename = self.web_path('%s-thumb.png' % diagram_name)
				svg_filename = self.web_path('%s.svg' % diagram_name)
				
				#maybe use: 'xrange="2006/04/04.22:00 2006/04/05.12:00"'
				ploticus_binary = 'ploticus' #but in non-debian distros might be "pl"
				ploticus_cmd_tmpl = ploticus_binary + '''\
 %s -prefab chron data="%s" header=yes x=1 y=2 %s \
datefmt=yyyy/mm/dd  xinc="1 day" mode=line unittype=datetime \
title="some statistics (still experimental)" -o "%s" %s 2>/dev/null''' # + 'xrange="2006/04/06.20:35 2006/04/06.21:15"'
#TODO: make ploticus command silent. -diagfile and -errfile doesn't prevent getting anoying messages about number of records and fields for records...
				cmd = ploticus_cmd_tmpl % ("-png", plotfilename, columns, png_filename, '')
				subprocess.call( cmd, shell=True) 

				cmd = ploticus_cmd_tmpl % ("-png", plotfilename, columns, png_thumbfilename, '-scale 0.3') 
				subprocess.call( cmd, shell=True) 

				cmd = ploticus_cmd_tmpl % ( "-svg", plotfilename, columns, svg_filename, '')
				subprocess.call( cmd, shell=True) 

				pngs.append('%s.png' % diagram_name)
				pngs_thumb.append('%s-thumb.png' % diagram_name)
				svgs.append('%s.svg' % diagram_name)
				images += [png_filename, png_thumbfilename, svg_filename]
			# write stats client page
			stats_html_filename = self.web_path('%s-stats.html' %client)
			f = open(stats_html_filename, 'w')
			f.write('<html><body>\n')
			for png, svg in zip(pngs, svgs):
				f.write('<h3>%s</h3> <img src="%s"> <p><a href="%s">svg</a></p>\n' % (png, png, svg) )
			f.write('</body></html>\n')
			f.close()
			images.append(stats_html_filename)
		return images, clients_with_stats
					


		
