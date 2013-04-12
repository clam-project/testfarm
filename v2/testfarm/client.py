import datetime

class Client(object) :

	def __init__(self, **kwds) :
		self._now = None
		self._config = kwds
#		self._reporters = MultiReporter()
#		self._reporters.add(NullReporter) # Ensures interface
#		self._reporters.add(ConsoleReporter) 
		pass

	@property
	def now(self) :
		if self._now is not None : return self._now
		return datetime.datetime.now()

	@now.setter
	def now(self, value) :
		self._now = value

	def subst(self, string) :
		return string.format(**self._config)

	"""
	def addReporter(self, reporter) :
		self._reporters = reporter

	def run(self ) :
		pass

	def addRepository(self, kind, **kwds) :
		self._reporters.add(kind(**kwds))

	def addTask(self, name, commands, critical=False, disabled=False) :
		pass
	"""
