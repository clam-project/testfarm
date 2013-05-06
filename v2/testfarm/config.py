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
		self.__dict__['_vars'] = kwds

	def __contains__(self, key) :
		return key in self._vars

	def __setattr__(self, key, value) :
		if key in self.__dict__ :
			return super(object, self).__setattr__(key,value)
		self._vars[key] = value

	def __getattr__(self, key) :
		try :
			return self._vars[key]
		except KeyError as e:
			raise AttributeError("'Config' object has no attribute '{0}'"
				.format(key))

	def subst(self, string) :
		return string.format(**self._vars)

	def load(self, filename) :
		loaded = loadDictFile(filename)
		self._vars.update(loaded)

	def dumps(self, classStyle=False) :
		def dumpSubConfigClassStyle(key, value, prefix) :
			subprefix = prefix + "\t"
			subline = "{0}class {1} :\n".format(prefix, key)
			return subline + "".join(dumpdict(value, subprefix))
		def dumpSubConfig(key, value, prefix) :
			subprefix = "{0}{1}.".format(prefix,key)
			subline = "{0}{1} = Config()\n".format(prefix, key)
			return subline + "".join(dumpdict(value, subprefix))
		if classStyle : dumpSubConfig = dumpSubConfigClassStyle
		def dumpdict(values, prefix='') :
			return [
				"{0}{1} = {2!r}\n".format(prefix, key, value)
				if not isinstance(value, dict) else
				dumpSubConfig(key, value, prefix)
				for key, value in sorted(values.iteritems()) ]

		return "".join(dumpdict(self._vars))



