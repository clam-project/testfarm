import sys
import socket
from listeners import NullResultListener

class IrcReporter(NullResultListener) :
	"""This listener sends reports to an ircbot which is listening
	at the provided address and port."""

	def __init__(self,
			project,
			client,
			channel,
			address,
			testfarm_page = None,
			port = 6667,
			nick='testfarm',
			ident='testfarm',
			realname='TestFarm Bot',
			) :
		self.__dict__.update(locals())

	def send(self, command, **kwds) :
		subst = vars(self)
		subst.update(kwds)
		self.socket.send(command.format(**subst))

	def listen_end_task(self, taskname, all_ok):
		color = 'GREEN' if all_ok else 'RED'

		try :
			self.socket=socket.socket()
			self.socket.connect((self.address, self.port)) #Connect to server
			self.send('NICK {nick}\r\n') #Send the nick to server
			self.send('USER {ident} {address} bla :{realname}\r\n') #Identify to server~
			self.send('JOIN {channel}\r\n')
			self.send('PRIVMSG {channel} : TestFarm for {project}::{client} is {color}\r\n', color=color)
			if self.testfarm_page :
				self.send('PRIVMSG {channel} : More info at {testfarm_page}\r\n')
			self.send('QUIT :bye\r\n')

			while self.socket.recv ( 4096 ) : pass

		except socket.error, e :
			print >> sys.stderr, "Error connect to irc:", e.message


if __name__ == "__main__":
	ircReporter = IrcReporter('localhost', 2222)
	ircReporter.listen_end_task('mytask', True)

