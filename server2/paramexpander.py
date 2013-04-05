import inspect

def expandfunction(expander) :
	def decorator(f) :
		g = expander
		gargs, gvarargs, gkeywords, gdefaults = inspect.getargspec(g)
		fargs, fvarargs, fkeywords, fdefaults = inspect.getargspec(f)
		wrapperSpec = inspect.formatargspec(fargs)
		wrapperSource = """\
def wrapper {wrapperSpec} :
	g {gcall}
	return f {fcall}
""".format(
	wrapperSpec = wrapperSpec,
	gcall = "()",
	fcall = "(a,b)",
	)
		exec wrapperSource in locals(), globals()
		return wrapper
	return decorator

def lala() :
		gargs, gvarargs, gkeywords, gdefaults = inspect.getargspec(g)
		fargs, fvarargs, fkeywords, fdefaults = inspect.getargspec(f)
