#!/usr/bin/python

import decorator
import inspect


def check_signature(signature, **kwd) :
	print "check_signature", signature, kwd

def check_signature2(signature, id, **kwd) :
	print "check_signature2", signature, id, kwd


def expand_decorator(expander) :
	"""
	Decorator that expands the decorated function argument
	specification with the one from expander function.
	For example if we have:
		original(a, b, c=1, *args1, **kwd1)
		expander(x, y, y=2, *args2, **kwd2)
	a expanded function will be created as:
		result(a, b, x, y, c=1, y=2, *args1, **kwd1)
	The expander function is called just before the decorated one.
	The exit value is the one of the decorated one.
	"""
	def decorator(decorated) :
		expanderfun = expander # required to create it as local
		targetargs = inspect.getargspec(decorated)
		expandargs = inspect.getargspec(expanderfun)
		# TODO: expander with optional
		wrapperspec = [
			arg for arg in expandargs.args
			if arg not in targetargs.args] + [
			inspect.formatargspec(*targetargs)[1:-1]
			]
		targetcall = ["%s=%s"%(arg,arg) for arg in targetargs.args]
		checkercall = targetcall+["%s=%s"%(arg,arg) for arg in expandargs.args]
		if targetargs.varargs : targetcall.append("*%s"%targetargs.varargs)
		if targetargs.keywords : targetcall.append("**%s"%targetargs.keywords)
		source = """\
def wrapper ({wrapperspec}) :
#	print "wrapper locals", locals()
	expanderfun({checkercall})
	return decorated({targetcall})
""".format(
			wrapperspec = ",".join(wrapperspec),
			checkercall=", ".join(checkercall),
			targetcall=", ".join(targetcall),
		)

		exec source in locals(), globals()
		return wrapper
	return decorator

if __name__ == "__main__" :
		@expand_decorator(check_signature2)
		def f(a,b=3, *pos, **kwd) :
			print a, b, pos, kwd

		f(signature="boo",id="tu",a=1,b=2,c=3,d=4)
		f("boo","tu","a","b",c=3,d=4)


