
header = """
<html>
<head>
<meta http-equiv="refresh" content="5">
<link href="style.css" rel="stylesheet" type="text/css">
<title>Tests Farm</title>
</head>
<body>
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

	def clean_log_files(self):
		open(self.logfile, "w")

	def time(self):
		return "15-03-2006 19:32:00"

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
		entry = "\n('BEGIN_REPOSITORY', '%s', '%s'),\n" % (repositoryname, self.time()) 
		open(self.logfile, "a+").write(entry)

	def listen_end_repository(self, repositoryname, status):
		entry = "('END_REPOSITORY', '%s', '%s', %s),\n" % (repositoryname, self.time(), status)
		open(self.logfile, "a+").write(entry)
	

class TestFarmServer:
	def __init__(self, serverlistener):
		self.serverlistener = serverlistener

	def iterations(self):
		log = eval("[ %s ]" % open(self.serverlistener.logfile).read() )
		result = []
		iteration_opened = False
		for entry in  log :
			tag = entry[0]
			if tag == 'BEGIN_REPOSITORY' :
				begin_time = entry[2]
				iteration_opened = True
			if tag == 'END_REPOSITORY' :
				end_time = entry[2]
				status_ok = entry[3]
				if status_ok :
					status = 'stable'
				else :
					status = 'broken'
				result.append( (begin_time, end_time, status) )
				iteration_opened = False
		if iteration_opened :
			result.append( (begin_time, '', 'inprogress') )
				
		return result
	def html_iterations(self):
		content = ''
		for begin_time, end_time, status in self.iterations():
			begin_time_html = "<p>%s</p>" % begin_time
			if end_time :
				end_time_html = "<p>%s</p>" % end_time
			else:
				end_time_html = "<p>in progres...</p>"
			details_html = '<p><a href="something=%s">details</a></p>' % begin_time
			content += '<div class="%s">\n%s\n%s\n%s\n</div>' % (status, begin_time_html, end_time_html, details_html)
		return header + content + footer
		
	'''
	def __init__(self):
		self.repository_state = None
		self.repository_html_log = ''
		self.details_log = "" 
		
	def repository_status_html(self, name=None):
		return "%(HEADER)s\n%(FOOTER)s"

	def repository_status_html2(self, name=None):
		status_html = "%(HEADER)s"
		status_html += "\n\t%s" % self.repository_html_log
		status_html += "\n%(FOOTER)s"
		return status_html

	def write_details_html_log(self) :
		details_html_log = "%(HEADER)s\n" % {'HEADER' : header_details}
		details_html_log += self.details_log
		details_html_log += "\n%(FOOTER)s" % {'FOOTER' : footer}
		open("foo2-details.html", "w").write( details_html_log )

	def listen_result(self, command, ok, output, info, stats):
		self.details_log += '\n\t\t<p id="command">%s' % command
		if ok :
			self.details_log += '\t<span id="command_ok">[OK]</span></p>'
		else :
			self.details_log += '\t<span id="command_failure">[FAILURE]</span>\t<span id="normal">%s</span></p>' % output
		
	def listen_begin_task(self, taskname):
		self.details_log += '\n\t\t<p id="task">BEGIN_TASK %s</p>' % taskname

	def listen_end_task(self, taskname):
		self.details_log += '\n\t\t<p id="task">END_TASK %s</p>' % taskname
	
	def listen_begin_repository(self, repositoryname):
		actual_datetime = datetime.datetime.now()
		self.begin_datetime = actual_datetime.strftime("%d-%m-%Y %H:%M:%S")
		self.details_log += """\t<div class="details">
		<p id="repository"> BEGIN_REPOSITORY %s </p>""" % repositoryname
		self.repository_state = 'progress'
		self.repository_html_log = "<h1>%s repository status</h1>\n" % repositoryname
		self.repository_html_log += "\t<div class="progress">\n<p><b>Begin:</b> %(BEGIN_DATETIME)s</p>\n</div>" 

		html_log = self.repository_status_html2() % {'HEADER' : header, 'FOOTER' : footer, 'BEGIN_DATETIME' : self.begin_datetime}
		
		open("foo2.html", "w").write( html_log )

	def listen_end_repository(self, repositoryname, status):
		actual_datetime = datetime.datetime.now()
		self.end_datetime = actual_datetime.strftime("%d-%m-%Y %H:%M:%S")
		self.details_log += """\n\t\t<p id="repository"> END_REPOSITORY %s</td></p>
	</div>""" % repositoryname
		if (status==True):
			self.repository_state = 'ok'
			self.repository_html_log = "<h1>%s repository status</h1>\n" % repositoryname
			self.repository_html_log += """\t<div class="ok">
		<p><b>Begin:</b> %(BEGIN_DATETIME)s</p>
		<p><b>End:</b> %(END_DATETIME)s</p>
		<p><a href="foo2-details.html">Show Details</a></p>
	</div>"""
		else:
			self.repository_state = 'failure'
			self.repository_html_log = "<h1>%s repository status</h1>\n" % repositoryname
			self.repository_html_log += """\t<div class="failure">
		<p><b>Begin:</b> %(BEGIN_DATETIME)s</p>
		<p><b>End:</b> %(END_DATETIME)s</p>
		<p><a href="foo2-details.html">Show Details</a></p>
	</div>"""
	
		html_log = self.repository_status_html2() % {'HEADER' : header, 'FOOTER' : footer, 'BEGIN_DATETIME' : self.begin_datetime, 'END_DATETIME': self.end_datetime}
		open("foo2.html", "w").write( html_log )
		self.write_details_html_log()
	'''


