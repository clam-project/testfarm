import inspect

def expandfunction(expander) :
	def decorator(f) :
		g = expander
		gargs, gvarargs, gkeywords, gdefaults = inspect.getargspec(g)
		fargs, fvarargs, fkeywords, fdefaults = inspect.getargspec(f)
		gdefaultvars = gargs[-len(gdefaults):] if gdefaults else []
		fdefaultvars = fargs[-len(fdefaults):] if fdefaults else []
		defaultvars = fdefaultvars + gdefaultvars
		keywords = fkeywords or gkeywords
		wrapperSpec = inspect.formatargspec(
			[arg for arg in fargs
				if arg not in defaultvars
			]+
			[arg for arg in gargs
				if  arg not in fargs
				and arg not in gdefaultvars
			]+
			([arg for arg in fdefaultvars])+
			([arg for arg in gdefaultvars
				if arg not in fdefaultvars]),
			None,
			keywords,
			list(fdefaults or []) + [
			value
			for var, value in zip(gdefaultvars, gdefaults or [])
			if var not in fdefaultvars]
			)
		gcall = [
				"{var}={var}".format(var=var)
				for var in gargs
			]
		if gkeywords :
			gcall += [
				"{var}={var}".format(var=var)
				for var in fargs
				if arg not in gargs
			]+["**{}".format(keywords)]
		fcall = [
				"{var}={var}".format(var=var)
				for var in fargs
			]
		if fkeywords :
			fcall += [
				"{var}={var}".format(var=var)
				for var in gargs
				if var not in fargs
			] + ["**{}".format(keywords) ]
		wrapperSource = """\
def wrapper {wrapperSpec} :
	g ({gcall})
	return f ({fcall})
""".format(
	wrapperSpec = wrapperSpec,
	gcall = ",".join(gcall),
	fcall = ",".join(fcall),
	)
		exec wrapperSource in locals(), globals()
		wrapper.__name__ = f.__name__
		wrapper.__doc__ = f.__doc__
		return wrapper
	return decorator

def lala() :
		gargs, gvarargs, gkeywords, gdefaults = inspect.getargspec(g)
		fargs, fvarargs, fkeywords, fdefaults = inspect.getargspec(f)
