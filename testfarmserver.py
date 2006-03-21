import datetime, os, glob, sys

header = """
<html>
<head>
<meta http-equiv="refresh" content="60">
<link href="style.css" rel="stylesheet" type="text/css">
<title>Tests Farm</title>
</head>
<body>
<h1>testfarm monitor</h1>
<p>this file is the default html log for all testfarm tasks (from any repository) </p>
"""

header_details = """
<html>
<head>
<link href="style.css" rel="stylesheet" type="text/css">
<title>Tests Farm Details</title>
</head>
<body>
"""

footer = """
</body>
</html>
"""

def remove_path_and_extension( path ):
	return os.path.splitext( os.path.basename( path ) )[0]

def log_filename(logs_base_dir, client_name) :
	return '%s/%s.testfarmlog' % (logs_base_dir, client_name)

def idle_log_filename(logs_base_dir, client_name) :
	return '%s/%s.idle' % (logs_base_dir, client_name)

def create_dir_if_needed(dir):
	if not os.path.isdir( dir ) :
		sys.stderr.write("Warning: directory '%s' is not available. Creating it." % dir)
		os.makedirs(dir)

#
#  LISTENER
#

class ServerListener:
	def __init__(self, 
		client_name='testing_client', 
		logs_base_dir = '/tmp/testfarm_logs',
	) :
		self.iterations_needs_update = True
		self.client_name = client_name
		self.logs_base_dir = logs_base_dir
		self.logfile = log_filename( logs_base_dir, client_name )
		self.idle_logfile = idle_log_filename( logs_base_dir, client_name )
		create_dir_if_needed( logs_base_dir )

		
	def __append_log_entry(self, entry) :
		open(self.logfile, 'a+').write( entry )

	def list_log_files(self):
		return glob.glob('%s/*' % self.logs_base_dir)

	def clean_log_files(self):
		for filename in self.list_log_files():
			os.remove(filename)
		open( self.logfile, "w")
		open( self.idle_logfile, "w")

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
	
	def listen_begin_repository(self, repositoryname):
		entry = "\n('BEGIN_REPOSITORY', '%s', '%s'),\n" % (repositoryname, self.current_time())
		self.__append_log_entry(entry)
		self.iterations_needs_update = True

	def listen_end_repository(self, repositoryname, status):
		entry = "('END_REPOSITORY', '%s', '%s', %s),\n" % (repositoryname, self.current_time(), status)
		self.__append_log_entry(entry)
		self.iterations_needs_update = True

	def iterations_updated(self):
		self.iterations_needs_update = False
	
	def listen_cms_is_idle(self, seconds_for_next_check):
		entry = "{date:'%s', next_run_interval:%d}" % (self.current_time(), seconds_for_next_check)
		open(self.idle_logfile, 'a+').write( entry )
	
	

#
#     SERVER
#

class TestFarmServer:
	def __init__(self, 
		logs_base_dir = '/tmp/testfarm_logs',
		html_dir = './html'
	) :
		self.logs_base_dir = logs_base_dir 
		self.html_dir = html_dir
		create_dir_if_needed( html_dir )

	def client_names(self):
		logfiles = glob.glob('%s/*.testfarmlog' % self.logs_base_dir )
		result = map( remove_path_and_extension, logfiles)
		return result

	def load_client_log(self, client_name):
		filename = log_filename( self.logs_base_dir, client_name )
		return eval("[ %s ]" % open( filename ).read() )

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
	
	def html_single_iteration_details(self, client_name, wanted_date):
		content = []
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
					content.append( '<p class="output"> OUTPUT: %s </p>' % entry[3] )
				if entry[4] :
					content.append( '<p class="info"> INFO: %s </p>' % entry[4] )
				if entry[5] :
					content.append(  '<p class="stats"> STATS: {%s} </p>' % ''.join(entry[5]) )
				content.append( '</div>' )

		return header_details + '\n'.join(content) + footer	

	'''#minimal version:
	def html_single_iteration_details(self, client_name, wanted_date):
		content = ["<pre>"]
		for entry in self.single_iteration_details(client_name, wanted_date ):
			content.append( "\n".join( map(str, entry) ) )	
		content.append("</pre>")
		return header_details + "\n".join(content) + footer
	'''

	def write_details_static_html_file(self, client_name, wanted_date):
		details = self.html_single_iteration_details(client_name, wanted_date)
		open("%s/details-%s-%s.html" % (self.html_dir, client_name, wanted_date), "w").write( details )
	
	def write_last_details_static_html_file(self): 
		for client in self.client_names():
			client_log = self.load_client_log(client)
			last_date = self.last_date(client_log)
			self.write_details_static_html_file(client, last_date)

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

	def iterations(self):
		result = {}
		for client_name in self.client_names():
			result[client_name] = self.__get_client_iterations(client_name)
		return result

	def __html_format_client_iterations(self, client_name, client_iterations):
		content = []
		for begintime_str, endtime_str, repo_name, status in client_iterations:
			name_html = "<p>%s</p>" % repo_name
			time_tags = ["Y", "M", "D", "hour", "min", "sec"]
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

	def html_iterations(self):
		iterations_dict = self.iterations()
		content = ['<table>\n<tr>']
		for client in iterations_dict.keys():
			content.append('<th> Client: %s </th>' % client )
		content.append('</tr>')
		
		for client in iterations_dict.keys():
			content.append('<td>')
			client_iterations = iterations_dict[client]
			content += self.__html_format_client_iterations(client, client_iterations) 
			content.append('</td>')
		content.append('</table>')
		return header + '\n'.join(content) + footer
		
	def write_iterations_static_html_file(self):
		open("%s/iterations.html" % self.html_dir, "w").write( self.html_iterations() )

	def update_static_html_files(self):
		self.write_last_details_static_html_file()
		self.write_iterations_static_html_file()
