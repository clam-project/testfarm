import inspect

def expandfunction(expander) :
	def decorator(f) :
		g = expander
		gargs, gvarargs, gkeywords, gdefaults = inspect.getargspec(g)
		fargs, fvarargs, fkeywords, fdefaults = inspect.getargspec(f)
		gdefaultvars = gargs[-len(gdefaults):] if gdefaults else []
		wrapperSpec = inspect.formatargspec(
			[arg for arg in fargs]+
			[arg for arg in gargs
				if  arg not in fargs
				and arg not in gdefaultvars
			]+
			([arg for arg in gdefaultvars]),
			None,
			None,
			gdefaults
			)
		gcall = ",".join((
			"{var}={var}".format(var=var)
			for var in gargs
			))
		wrapperSource = """\
def wrapper {wrapperSpec} :
	g ({gcall})
	return f ({fcall})
""".format(
	wrapperSpec = wrapperSpec,
	gcall = gcall,
	fcall = "a,b",
	)
		exec wrapperSource in locals(), globals()
		wrapper.__name__ = f.__name__
		wrapper.__doc__ = f.__doc__
		return wrapper
	return decorator

def lala() :
		gargs, gvarargs, gkeywords, gdefaults = inspect.getargspec(g)
		fargs, fvarargs, fkeywords, fdefaults = inspect.getargspec(f)
