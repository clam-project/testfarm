import datetime
header = """
<html>
<head>
<!-- <meta http-equiv="refresh" content="5"> -->
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


class ServerListener:
	def __init__(self):
		self.logfile = "/tmp/tasks.log"
		self.iterations_needs_update = True

	def clean_log_files(self):
		open(self.logfile, "w")

	def current_time(self):
		return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

	def listen_result(self, command, ok, output, info, stats):
		entry = str( ('CMD', command, ok, output, info, stats) ) + ',\n'
		open(self.logfile, "a+").write(entry)

	def listen_begin_task(self, taskname):
		entry = "('BEGIN_TASK', '%s'),\n" % taskname 
		open(self.logfile, "a+").write(entry)

	def listen_end_task(self, taskname):
		entry = "('END_TASK', '%s'),\n" % taskname
		open(self.logfile, "a+").write(entry)
	
	def listen_begin_repository(self, repositoryname):
		entry = "\n('BEGIN_REPOSITORY', '%s', '%s'),\n" % (repositoryname, self.current_time()) 
		open(self.logfile, "a+").write(entry)
		self.iterations_needs_update = True

	def listen_end_repository(self, repositoryname, status):
		entry = "('END_REPOSITORY', '%s', '%s', %s),\n" % (repositoryname, self.current_time(), status)
		open(self.logfile, "a+").write(entry)
		self.iterations_needs_update = True
	def iterations_updated(self):
		self.iterations_needs_update = False
	

class TestFarmServer:
	def __init__(self, serverlistener):
		self.serverlistener = serverlistener

	def load_log(self):
		return eval("[ %s ]" % open(self.serverlistener.logfile).read() )

	def last_date(self, log):
		log.reverse()
		for entry in log :
			tag = entry[0]
			if tag == 'BEGIN_REPOSITORY':
				return entry[2]
		assert "BEGIN_REPOSITORY not found"
		
	def single_iteration_details(self, wanted_date):
		log = self.load_log()
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

	def write_html_detail_file(self, wanted_date):
		open("details-%s" % wanted_date, "w").write( self.html_single_iteration_details(wanted_date) )

	def html_single_iteration_details(self, wanted_date):
		content = ["<pre>"]
		for entry in self.single_iteration_details( wanted_date ):
			content.append( "\n".join( map(str, entry) ) )	
		content.append("</pre>")
		return header_details + "\n".join(content) + footer

	def write_single_iteration_details_html_file(self, wanted_date):
		details = self.html_single_iteration_details(wanted_date)
		open("details-%s.html" % wanted_date, "w").write( details )
	
	def write_last_single_iteration_details_html_file(self): #TODO remove
		log = self.load_log()
		last_date = self.last_date(log)
		self.write_single_iteration_details_html_file(last_date)

	def iterations(self):
		log = self.load_log()
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

	def html_iterations(self):
		content = ''
		for begintime_str, endtime_str, repo_name, status in self.iterations():
			name_html = "<p>%s</p>" % repo_name
			time_tags = ["Y", "M", "D", "hour", "min", "sec"]
			begintime_dict = dict(zip( time_tags, begintime_str.split("-") ))
			begintime_html = "<p>Begin time: %(hour)s:%(min)s:%(sec)s</p>" % begintime_dict
			if endtime_str :
				endtime_dict = dict(zip( time_tags, endtime_str.split("-") ))
				endtime_html = "<p>End time: %(hour)s:%(min)s:%(sec)s</p>" % endtime_dict
			else:
				endtime_html = "<p>in progres...</p>"
			details_html = '<p><a href="details-%s.html">details</a></p>' % begintime_str
			content += '<div class="%s">\n%s\n%s\n%s\n%s\n</div>' % (status, name_html, begintime_html, endtime_html, details_html)
		return header + content + footer
		
	def write_iterations_html_file(self):
		open("iterations.html", "w").write( self.html_iterations() )

	def update_static_html_files(self):
		self.write_last_single_iteration_details_html_file()
		if self.iterations_html_needs_update:
			self.write_iterations_html_file()
