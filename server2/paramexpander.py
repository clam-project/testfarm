import inspect

def expandfunction(expander) :
	def decorator(f) :
		g = expander
		gargs, gvarargs, gkeywords, gdefaults = inspect.getargspec(g)
		fargs, fvarargs, fkeywords, fdefaults = inspect.getargspec(f)
		wrapperSpec = inspect.formatargspec(fargs)
		wrapperSource = """\
def wrapper {wrapperSpec} :
	g()
	return f(a,b)
""".format(
	wrapperSpec = wrapperSpec,
	)
		exec wrapperSource in locals(), globals()
		return wrapper
	return decorator

def lala() :
		gargs, gvarargs, gkeywords, gdefaults = inspect.getargspec(g)
		fargs, fvarargs, fkeywords, fdefaults = inspect.getargspec(f)
