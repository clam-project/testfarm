
import sys, os, subprocess
from time import gmtime, strftime

import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Encoders import encode_base64
from listeners import NullResultListener



# returns true if state changed
def check_state_changed(color, repositories):
	def write_state(current_time, filename, color, repositories):
		print current_time, color, "%s"%repositories
		file = open(filename, 'w')
		file.write(current_time+'\n')
		file.write(color+'\n')
		file.write("%s"%repositories+'\n')

	base_path = os.path.expanduser("~")
	file_name = base_path+"/.testfarm_state"
	current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

	if not os.path.exists(file_name) :
		write_state(current_time, file_name, color, repositories)

	file = open(file_name, 'r')
	old_values = file.readlines()

	repositories_changed = []
	repositories_changed = set(eval(old_values[2])) - set(repositories)

	if len(repositories_changed) == 0: # nothing changed, so use the current one
		repositories_changed = repositories

	write_state(current_time, file_name, color, repositories)

	#print color, old_values
	old_color = old_values[1].rstrip()
	return old_color, repositories_changed


class MailReporter(NullResultListener) :
	def __init__(self,
		recipients,
		server,
		username,
		password,
		testfarm_page=None,
		port=587,
		from_email = 'noreply@nodomain.com',
		from_name = 'Testfarm Report',
		subject = 'Testfarm is %s',
		**kwd
		) :
		self.repositories = []

		self.server = server
		self.port = port
		self.username = username
		self.password = password
		self.from_email = from_email
		self.from_name = from_name
		self.recipients = recipients
		self.testfarm_page = testfarm_page
		self.subject = subject

	def listen_task_info(self, task):
		self.task = task

	def listen_begin_task(self, taskname, snapshot) :
		self.repositories = snapshot


	def listen_end_task(self, taskname, all_ok):
		color = 'GREEN' if all_ok else 'RED'
		last_color, last_commits  = check_state_changed(color, self.repositories)
		msg = "The current state is %s \n\n" % (color)


		repositories = last_commits if len(last_commits) != 0 else self.repositories
		for (repos,rev,committer) in repositories:
			msg += "- repository: \'%s\', last commit by %s \n" % (repos,committer)

		if not all_ok or last_color == 'RED' :
			# whenever is red or changed from red to green
			if color == 'RED' and self.testfarm_page :
				msg += '\n\nCheck the testfarm page for the specific error: %s\n'%self.testfarm_page
			self.send_mail(self.subject%color, msg)

	def send_mail(self, subject, message, debug=0):
		msg = MIMEMultipart()
		msg['From'] = self.from_name
		msg['To'] = self.recipients
		msg['Subject'] = subject
		msg.attach(MIMEText(message))

		server = smtplib.SMTP(self.server, self.port)
		server.set_debuglevel(debug)

		try:
			server.ehlo()
			# If we can encrypt this session, do it
			if server.has_extn('STARTTLS'):
				server.starttls()
				server.ehlo() # re-identify ourselves over TLS connection
			server.login(self.username, self.password)
			recipient_list = [r.strip() for r in self.recipients.split(",") ]
			smtpresult = server.sendmail(self.from_email, recipient_list, msg.as_string())
			if not smtpresult : return # ok!
			for recipient, error in smtpresult.iteritems():
				print  """Could not delivery mail to: %s, server said: %s %s"""  \
					% (recip, smtpresult[recip][0], smtpresult[recip][1])

		finally:
			server.quit()


if __name__ == "__main__":
	m=MailReporter()
	m.send_mail('GREEN', 'this is a test message', 1)

	#import time
	#time.sleep(1)
	#print check_state_changed('GREEN', '1', 'x')
	#time.sleep(1)
	#print check_state_changed('GREEN', '1', 'x')
	#time.sleep(1)
	#print check_state_changed('RED', '1', 'x')



