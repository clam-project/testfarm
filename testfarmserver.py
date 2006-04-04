#
#  Copyright (c) 2006 Pau Arumí, Bram de Jong, Mohamed Sordo 
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

import datetime, os, glob, sys
import subprocess
 
header_index = """
<html>
<head>
<meta http-equiv="refresh" content="30">
<link href="style.css" rel="stylesheet" type="text/css">
<title>Tests Farm for project %(repository_name)s </title>
</head>
<body>
<h1>testfarm for project %(repository_name)s </h1>

"""

header_details = """
<html>
<head>
<link href="style.css" rel="stylesheet" type="text/css">
<title>Tests Farm Details</title>
<script type="text/javascript" language="JavaScript" src="testfarm.js"></script>
</head>
<body>
"""

footer = """
<p>TestFarm is free software. Learn <a href="www.iua.upf.es/~parumi/testfarm">about TestFarm</a>.</p>
</body>
</html>
"""

def remove_path_and_extension( path ):
	return os.path.splitext( os.path.basename( path ) )[0]

def log_filename(logs_base_dir, repository_name, client_name) :
	return '%s/%s/%s.testfarmlog' % (logs_base_dir, repository_name, client_name)

def idle_filename(logs_base_dir, repository_name, client_name) :
	return '%s/%s/%s.idle' % (logs_base_dir, repository_name, client_name)

def create_dir_if_needed(dir):
	if not os.path.isdir( dir ) :
		sys.stderr.write("\nWarning: directory '%s' is not available. Creating it." % dir)
		os.makedirs(dir)

#
#  LISTENER
#

class ServerListener:
	def __init__(self, 
		client_name='testing_client', 
		logs_base_dir = '/tmp/testfarm_tests',
		repository_name=None
	) :
		self.iterations_needs_update = True
		self.client_name = client_name
		self.repository_name = repository_name
		self.logs_base_dir = logs_base_dir
		self.logfile = None
		self.idle_file = None
		
		assert repository_name, "Error, repository_name was expected"

		create_dir_if_needed( "%s/%s" % (self.logs_base_dir, repository_name) ) 
		self.logfile = log_filename( self.logs_base_dir, repository_name, self.client_name )
		self.idle_file = idle_filename( self.logs_base_dir, repository_name, self.client_name )

		
	def __append_log_entry(self, entry) :
		f = open(self.logfile, 'a+')
		f.write( entry )
		f.close()
	def __write_idle_info(self, idle_info) :
		f = open(self.idle_file, 'w')
		f.write( idle_info )
		f.close()

	def clean_log_files(self):
		subprocess.call('rm -rf %s' % self.logs_base_dir, shell=True)

	def current_time(self):
		return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

	def listen_result(self, command, ok, output, info, stats):
		entry = str( ('CMD', command, ok, output, info, stats) ) + ',\n'
		self.__append_log_entry(entry)

	def listen_begin_task(self, taskname):
		entry = "('BEGIN_TASK', '%s'),\n" % taskname 
		self.__append_log_entry(entry)

	def listen_end_task(self, taskname):
		entry = "('END_TASK', '%s'),\n" % taskname
		self.__append_log_entry(entry)
	
	def listen_begin_repository(self, repository_name):
		entry = "\n('BEGIN_REPOSITORY', '%s', '%s'),\n" % (repository_name, self.current_time())
		self.iterations_needs_update = True
		self.__append_log_entry(entry)

	def listen_end_repository(self, repository_name, status):
		entry = "('END_REPOSITORY', '%s', '%s', %s),\n" % (repository_name, self.current_time(), status)
		self.__append_log_entry(entry)
		self.iterations_needs_update = True

	def iterations_updated(self):
		self.iterations_needs_update = False
	
	def listen_found_new_commits(self,  new_commits_found, next_run_in_seconds ):
		idle_dict = {}
		idle_dict['new_commits_found'] = new_commits_found
		idle_dict['date'] = self.current_time()
		idle_dict['next_run_in_seconds']=next_run_in_seconds	
		self.__write_idle_info( str( idle_dict ) )
	
	

#
#     SERVER
#
class TestFarmServer:
	def __init__(self, 
		logs_base_dir = '/tmp/testfarm_tests',
		html_base_dir = '/tmp/testfarm_html',
		repository_name = None
	) :
		self.logs_base_dir = logs_base_dir 
		self.html_base_dir = html_base_dir
		create_dir_if_needed( html_base_dir )
		if repository_name: #TODO not very sure of this  (PA)
			create_dir_if_needed( '%s/%s' % (html_base_dir, repository_name) )
			self.repository_name = repository_name
		else:
			print 'Warning: html dir was not created because Server was not initialized with a repository_name'
	
		
	def client_names(self):
		assert self.repository_name, "Error, repository_name was expected. But was None"
		logfiles = glob.glob('%s/%s/*.testfarmlog' % (self.logs_base_dir, self.repository_name) )
		result = map( remove_path_and_extension, logfiles)
		return result

	def load_client_log(self, client_name):
		filename = log_filename( self.logs_base_dir, self.repository_name, client_name )
		return eval("[ %s ]" % open( filename ).read() )

	def load_client_idle(self, client_name):
		filename = idle_filename( self.logs_base_dir, self.repository_name, client_name )
		try :
			content = open( filename ).read() 
		except IOError:
			return {}
		if not content :
			return {}
		return eval( content )

	def last_date(self, log):
		log.reverse()
		for entry in log :
			tag = entry[0]
			if tag == 'BEGIN_REPOSITORY':
				return entry[2]
		assert "BEGIN_REPOSITORY not found"

	def single_iteration_details(self, client_name, wanted_date):
		log = self.load_client_log(client_name)
		result = []
		in_wanted_iteration = False
		for entry in log :
			tag = entry[0]
			if not in_wanted_iteration :
				if tag == 'BEGIN_REPOSITORY' and entry[2] == wanted_date :
					in_wanted_iteration = True
			if in_wanted_iteration :
				result.append(entry)
				if tag == 'END_REPOSITORY' :
					in_wanted_iteration = False
					break
		return result
	
	def __html_single_iteration_details(self, client_name, wanted_date):
		content = []
		id_info = 1; # auto-increment id
		id_output = 1; # auto-increment id
		for entry in self.single_iteration_details(client_name, wanted_date ):
			tag = entry[0]
			if tag == 'BEGIN_REPOSITORY':
				content.append('<div class="repository"> BEGIN_REPOSITORY "%s" %s' % (entry[1], entry[2]) )
			elif tag == 'BEGIN_TASK':
				content.append('<div class="task"> BEGIN_TASK "%s"' % entry[1])
			elif tag == 'END_TASK':
				content.append('END_TASK "%s"</div>' % entry[1])
			elif tag == 'END_REPOSITORY':
				content.append( 'END_REPOSITORY "%s" %s %s</div>' % ( entry[1], entry[2], entry[3]) )
			else:
				assert tag == 'CMD', 'Log Parsing Error. Expected CMD, but was:' + entry
				content.append( '<div class=command>' )
				content.append( '<span class="command_string"> %s </span>' % entry[1] )
				if entry[2]:
					content.append( '<span class="command_ok">[OK]</span>' )
				else:
					content.append( '<span class="command_failure">[FAILURE]</span>' )
					content.append( '<p id="output%d" class="output"> OUTPUT: %s </p>' % ( id_output, entry[3] ) )
					content.append( ' <script type="text/javascript">togglesize(\'output%d\');</script> ' % id_output )
					id_output += 1
				if entry[4] :
					content.append( '<p id="info%d" class="info"> INFO: %s </p>' % ( id_info, entry[4] ) )
					content.append( ' <script type="text/javascript">togglesize(\'info%d\');</script> ' % id_info )
					id_info += 1
				if entry[5] :
					content.append(  '<p class="stats"> STATS: {%s} </p>' % ''.join(entry[5]) )
				content.append( '</div>' )

		return header_details + '\n'.join(content) + footer	

	'''
	#minimal version:
	def html_single_iteration_details(self, client_name, wanted_date):
		content = ["<pre>"]
		for entry in self.single_iteration_details(client_name, wanted_date ):
			content.append( "\n".join( map(str, entry) ) )	
		content.append("</pre>")
		return header_details + "\n".join(content) + footer
	'''

	def __write_details_static_html_file(self, client_name, wanted_date):
		details = self.__html_single_iteration_details(client_name, wanted_date)
		filename = "%s/%s/details-%s-%s.html" % (
			self.html_base_dir, 
			self.repository_name, 
			client_name, 
			wanted_date )
		f = open( filename, 'w' )
		f.write( details )
		f.close()
		return filename
	
	def __write_last_details_static_html_file(self):
		filenames = []
		for client in self.client_names():
			client_log = self.load_client_log(client)
			last_date = self.last_date(client_log)
			filename = self.__write_details_static_html_file(client, last_date)
			filenames.append(filename)
		return filenames

	def __get_client_iterations(self, client_name):
		log = self.load_client_log(client_name)
		iterations = []
		iteration_opened = False
		for entry in  log :
			tag = entry[0]
			if tag == 'BEGIN_REPOSITORY' :
				repo_name = entry[1]
				begin_time = entry[2]
				iteration_opened = True
			if tag == 'END_REPOSITORY' :
				end_time = entry[2]
				status_ok = entry[3]
				if status_ok :
					status = 'stable'
					pass
				else :
					status = 'broken'
				iterations.append( (begin_time, end_time, repo_name, status) )
				iteration_opened = False
		if iteration_opened :
			iterations.append( (begin_time, '', repo_name, 'inprogress') )
				
		iterations.reverse()
		return iterations

	def __get_client_stats(self, client_name):
		log = self.load_client_log(client_name)
		allstats = { 'time':[] }
		begin_time = ''
		for entry in log :
			tag = entry[0]
			if tag == 'BEGIN_REPOSITORY':
				begin_time = entry[2]
			if tag == 'CMD' :
				assert begin_time, "Error. found a stat before a begin_repository"
				stats_entry = entry[5]
				if not stats_entry:
					continue
				for key in stats_entry.keys():
					if not allstats.has_key(key):
						allstats[key] = []
					allstats[key].append( stats_entry[key] )
				allstats['time'].append( begin_time )
		return allstats

	def idle(self):
		result = {}
		for client_name in self.client_names():
			idle_entry = self.load_client_idle(client_name)
			result[client_name] = idle_entry
		return result

	def iterations(self):
		result = {}
		for client_name in self.client_names():
			result[client_name] = self.__get_client_iterations(client_name)
		return result

	def __html_format_client_iterations(self, client_name, client_idle, client_iterations):
		content = []
		time_tags = ["Y", "M", "D", "hour", "min", "sec"]
		if client_idle and not client_idle['new_commits_found'] :
			idlechecktime_str = client_idle['date']
			idlechecktime_dict = dict(zip( time_tags, idlechecktime_str.split("-") ))
			client_idle['date'] = "<p>Last check done at : %(hour)s:%(min)s:%(sec)s</p>" % idlechecktime_dict
			content.append('''\
<div class="idle">
%(date)s
<p>Next run after %(next_run_in_seconds)s seconds </p>
</div>''' % client_idle)

		for begintime_str, endtime_str, repo_name, status in client_iterations:
			name_html = "<p>%s</p>" % repo_name
			begintime_dict = dict(zip( time_tags, begintime_str.split("-") ))
			begintime_html = "<p>Begin time: %(hour)s:%(min)s:%(sec)s</p>" % begintime_dict
			if endtime_str :
				endtime_dict = dict(zip( time_tags, endtime_str.split("-") ))
				endtime_html = "<p>End time: %(hour)s:%(min)s:%(sec)s</p>" % endtime_dict
			else:
				endtime_html = "<p>in progres...</p>"
			details_html = '<p><a href="details-%s-%s.html">details</a></p>' % (client_name, begintime_str)
			content.append( '<div class="%s">\n%s\n%s\n%s\n%s\n</div>' % (
				status, name_html, begintime_html, endtime_html, details_html) )
		return content

	def __html_index(self, clients_with_stats):
		iterations_per_client = self.iterations()
		idle_per_client = self.idle()
		content = ['<table>\n<tr>']
		for client in iterations_per_client.keys():
			content.append('<th> Client: %s </th>' % client )
		content.append('</tr>')

		content.append('<tr>')
		for client in iterations_per_client.keys():
			if client in clients_with_stats:
				thumb_html = '<a target="_blank" href="%s.png"><img src="%s-thumb.png" /></a> <a href="%s.svg">svg</a>' % (client, client, client)
				
			else:
				thumb_html = ''
			content.append('<td style="text-align:center"> %s </td>' % thumb_html)
		content.append('</tr>')
			

		for client in iterations_per_client.keys():
			content.append('<td>')
			client_iterations = iterations_per_client[client]
			client_idle = idle_per_client[client]
			content += self.__html_format_client_iterations(client, client_idle, client_iterations) 
			content.append('</td>')
		content.append('</table>')
		return header_index % {'repository_name':self.repository_name} + '\n'.join(content) + footer
		
	def __write_html_index(self, clients_with_stats):
		filename = "%s/%s/index.html" % (	
			self.html_base_dir, 
			self.repository_name )
		f = open( filename, 'w' )
		f.write( self.__html_index( clients_with_stats ) )
		f.close()
		return filename

	def __helper_apache_log(self, msg):
			from mod_python import apache
			apache.log_error('TestFarm: out '+ str(out) )
		
	def update_static_html_files(self):
		newfiles, clients_with_stats = self.plot_stats()
		newfiles += self.__write_last_details_static_html_file()
		newfiles.append( self.__write_html_index( clients_with_stats ) )
		if self.repository_name == 'CLAM': #TODO the proper way
			filesstr = ' '.join(newfiles)
			out = subprocess.call('scp %s clamadm@www.iua.upf.es:testfarm/' % filesstr, shell=True)
			sys.stderr.write(str(out))
#			self.__helper_apache_log('TestFarm: sended: %s \nout: %s ' % (filesstr, str(out)) )

	def collect_stats(self):
		result = {}
		for client in self.client_names():
			result[client] = self.__get_client_stats(client)
		return result
	def __assert_all_keys_equal_length(self, stats, length):
		keys = stats.keys()
		for key in keys:
			assert length == len(stats[key]), "Error found stat with diferent length. key: %s\n%s" %(key, stats)

	def __format_datetime(self, time_str, pattern):
		time_tags = ["Y", "M", "D", "hour", "min", "sec"] #TODO move to attribute
		time_dict = dict(zip( time_tags, time_str.split("-") ))
		return pattern % time_dict 

	def plot_stats(self):
		allclients_stats = self.collect_stats()
		clients = allclients_stats.keys()
		images = []
		clients_with_stats = []
		for client in clients:
			stats = allclients_stats[ client ]
			keys = stats.keys()
			if len(keys)>1: #more fields than just 'time'
				clients_with_stats.append( client )
			length = len( stats[ keys[0] ] )
			self.__assert_all_keys_equal_length(stats, length)

			ploticus_data_filename = '%s/%s/%s.plot' % (self.logs_base_dir, self.repository_name, client)
			print 'writing file:', ploticus_data_filename
			f = open(ploticus_data_filename, 'w')
			f.write("time")
			# Write header
			for key in keys:
				if key == 'time': continue
				f.write("\t%s" % key)
			f.write("\n")
				
			for i in range(length):
				time_str = stats['time'][i]
				time_formatted = self.__format_datetime(time_str, "%(Y)s/%(M)s/%(D)s.%(hour)s:%(min)s")
				f.write(time_formatted)
				for key in keys:
					if key == 'time': continue
					f.write("\t%s" % stats[key][i])
				f.write('\n')
			f.close()

			columns = ""
			for i in range(len(keys)-2): # the first column is time, and the second is "y=1" already in the ploticus_cmd
				columns += " y%d=%d" % (i+2, i+3) # y2=3 y3=4, etc.

			png_filename = '%s/%s/%s.png' % (self.html_base_dir, self.repository_name, client)
			png_thumbfilename = '%s/%s/%s-thumb.png' % (self.html_base_dir, self.repository_name, client)
			svg_filename = '%s/%s/%s.svg' % (self.html_base_dir, self.repository_name, client)
			ploticus_cmd_tmpl = '''\
ploticus %s -prefab chron data=%s header=yes x=1 y=2 %s \
datefmt=yyyy/mm/dd  xinc="1 day" mode=line unittype=datetime\
title="some statistics (still experimental)" autow=yes -o %s '''
			
			ploticus_cmd_tmpl = '''\
ploticus %s -prefab chron data=%s header=yes x=1 y=2 %s \
datefmt=yyyy/mm/dd  mode=line unittype=datetime\
title="some statistics (still experimental)" xrange="2006/04/04.21:00 2006/04/04.23:30" -o %s '''
			subprocess.call(ploticus_cmd_tmpl % ( 
				"-png", ploticus_data_filename, columns, png_filename), shell=True )
			subprocess.call( (ploticus_cmd_tmpl + '-scale 0.4') % ( 
				"-png", ploticus_data_filename, columns, png_thumbfilename), shell=True )
			subprocess.call(ploticus_cmd_tmpl % ( 
				"-svg", ploticus_data_filename, columns, svg_filename), shell=True )
			images += [png_filename, png_thumbfilename, svg_filename]

		return images, clients_with_stats

		
