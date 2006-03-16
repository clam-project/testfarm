
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
	def time(self):
		return "15-03-2006 19:32:00"

	def listen_result(self, command, ok, output, info, stats):
		if ok :
			status_text = "ok"
		else :
			status_text = "failure"
		open(self.logfile, "a+").write("%s\n" % str( (command, status_text, output, info, stats) ) )

	def listen_begin_task(self, taskname):
		open(self.logfile, "a+").write("BEGIN_TASK %s\n" % taskname )

	def listen_end_task(self, taskname):
		open(self.logfile, "a+").write("END_TASK %s\n" % taskname )
	
	def listen_begin_repository(self, repositoryname):
		open(self.logfile, "a+").write("BEGIN_REPOSITORY %s\n%s\n" % (repositoryname, self.time()) )

	def listen_end_repository(self, repositoryname, status):
		open(self.logfile, "a+").write("END_REPOSITORY %s\n%s\n\n" % (repositoryname, self.time()) )
	

class TestFarmServer:
	def __init__(self):
		self.repository_state = None
		self.repository_html_log = ''
		self.details_log = "" 
		
	def repository_status_html(self, name=None):
		return """%(HEADER)s
%(FOOTER)s"""

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
		self.repository_html_log += """\t<div class="progress">
		<p><b>Begin:</b> %(BEGIN_DATETIME)s</p>
	</div>""" 

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


