import inspect

def expandfunction(expander) :
	def decorator(f) :
		g = expander
		gargs, gvarargs, gkeywords, gdefaults = inspect.getargspec(g)
		fargs, fvarargs, fkeywords, fdefaults = inspect.getargspec(f)
		goptional = gargs[-len(gdefaults):] if gdefaults else []
		foptional = fargs[-len(fdefaults):] if fdefaults else []
		alloptional = foptional + goptional
		keywords = fkeywords or gkeywords
		def keywordArgs(args) :
			return [
				"{var}={var}".format(var=var)
				for var in args
				]
		wrapperSpec = inspect.formatargspec(
			[
				# mandatory args from f
				arg for arg in fargs
				if  arg not in foptional
				and arg not in goptional
			] + [
				# mandatory args from g not in f
				arg for arg in gargs
				if  arg not in goptional
				and arg not in fargs
			] +
				foptional
			+ [
				arg for arg in goptional
				if arg not in foptional
			],
			None,
			keywords,
			list(fdefaults or []) + [
			value
			for var, value in zip(goptional, gdefaults or [])
			if var not in foptional]
			)
		allCallArgs = keywordArgs(set(gargs+fargs)) + [
			"**{0}".format(keywords) ]
		gcall = allCallArgs if gkeywords else keywordArgs(gargs)
		fcall = allCallArgs if fkeywords else keywordArgs(fargs)
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



