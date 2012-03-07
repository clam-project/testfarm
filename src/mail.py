
import sys, os, subprocess
from time import gmtime, strftime

import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Encoders import encode_base64


def _get_last_committers(repositories):
	def _run_cmd(command):
		output = []
		pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		while True:
			tmp = pipe.stdout.readline()	
			output.append( tmp )
			if pipe.poll() is not None:
				for line in pipe.stdout :
					output.append(line)
				break	
		status = pipe.wait()
	
		return (''.join(output), status)

	last_commits = []
	for repos,rev,_ in repositories:
		cdrepos = "cd ~/%s && "%repos
		committer, _ = _run_cmd(cdrepos+"svn info -rHEAD | grep Author: | while read a b c d; do echo $d; done")
		last_committer = committer.strip()
		if last_committer is not None and len(last_committer.split())>1 : # svn command was error
			last_committer=""

		last_commits.append((repos,rev,last_committer))

	return last_commits

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

	#last_commits = []
	#if len(repositories_changed) != 0:
	#	last_commits = _get_last_committers(repositories_changed)

	write_state(current_time, file_name, color, repositories)

	#print color, old_values
	old_color = old_values[1].rstrip()
	return old_color, repositories_changed


def send_mail(color, message, debug=0):
	try:
		import mailconfig
	except ImportError: 
		return
	server = smtplib.SMTP(mailconfig.server, mailconfig.port)
	server.set_debuglevel(debug)
		
	msg = MIMEMultipart()
	msg['From'] = mailconfig.from_name
	msg['To'] = mailconfig.to_email
	msg['Subject'] = mailconfig.subject%color
	text = message
	if color == 'RED' and mailconfig.testfarm_page :
		text += '\n\nCheck the testfarm page for the specific error: %s\n'%mailconfig.testfarm_page
	msg.attach(MIMEText(text))

	try:
		server.ehlo()
		# If we can encrypt this session, do it
		if server.has_extn('STARTTLS'):
			server.starttls()
			server.ehlo() # re-identify ourselves over TLS connection
			server.login(mailconfig.username, mailconfig.password)
			smtpresult = server.sendmail(mailconfig.from_email, mailconfig.to_email, msg.as_string())
			if smtpresult:
				for recip in smtpresult.keys():
					print  """Could not delivery mail to: %s Server said: %s %s"""  \
						% (recip, smtpresult[recip][0], smtpresult[recip][1])

	finally:
    		server.quit()

if __name__ == "__main__":
	send_mail('GREEN', 'this is a test message', 1)

	#import time
	#time.sleep(1)
	#print check_state_changed('GREEN', '1', 'x')
	#time.sleep(1)
	#print check_state_changed('GREEN', '1', 'x')
	#time.sleep(1)
	#print check_state_changed('RED', '1', 'x')



