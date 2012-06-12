
from listeners import NullResultListener

class IrcBotReporter(NullResultListener) :
	"""This listener sends reports to an ircbot which is listening
	at the provided address and port."""

	def __init__(self, address = 'localhost', port=2222) :
		self.address = address
		self.port = port

	def listen_end_task(self, taskname, all_ok):
		# TODO: Send 
		color = 'GREEN' if all_ok else 'RED'
		msg = "TestFarm is %s \n\n" % (color)
		import socket
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.address, self.port))
		s.send(msg)
		s.close()


if __name__ == "__main__":
	botReporter = IrcBotReporter('localhost', 2222)
	botReporter.listen_end_task('mytask', True)


