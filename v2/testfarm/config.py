import datetime

def loadDictFile(dictfile) :
	""" Returns a dict with the variables defined in a file """
	class temp : exec(open(dictfile))
	loaded = dict(temp.__dict__)
	del loaded['__doc__']
	del loaded['__module__']
	return loaded

class Config(object) :

	def __init__(self, **kwds) :
		self._vars = kwds
		vars(self).update(kwds)

	def __contains__(self, key) :
		return key in vars(self)

	def __setattr__(self, key, value) :
		vars(self)[key] = value
		self._vars[key] = value

	def subst(self, string) :
		return string.format(**vars(self))

	def load(self, filename) :
		loaded = loadDictFile(filename)
		vars(self).update(loaded)
		self._vars.update(loaded)




