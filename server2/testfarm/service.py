#!/usr/bin/env python
"""
Copyright 2007-2012 David Garcia Garzon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import webob
import sys, os
import decorator

class HttpError(Exception) :
	def __init__(self, status, message) :
		self.status = status
		self.message = message

class NotFound(HttpError) :
	def __init__(self, message) :
		HttpError.__init__(self, "404 Not Found", message)

class Forbidden(HttpError) :
	def __init__(self, message) :
		HttpError.__init__(self, "403 Forbidden", message)

class BadRequest(HttpError) :
	def __init__(self, message) :
		HttpError.__init__(self, "400 Bad Request", message)

class query(object) :
	"""Decorator to enhance functions"""
	def __init__(self, content_type='text/plain') :
		self.content_type = content_type

	def __call__(self, f, **kw) :
		f.content_type = self.content_type
		return f
		def wrapper(*args, **kwd) :
			return f(*args, **kwd)
		wrapper.__name__ = f.__name__
		wrapper.__doc__ = f.__doc__
		wrapper.__dict__.update(f.__dict__)
		return wrapper

class Reload:
	""" Module reload middleware """

	def __init__(self, app):
		# TODO: Check is one of our apps
		self.app = app
		self.mtimes = mtimes = {}
		for name in self.app._modules:
			__import__(name)
			moduleFile = sys.modules[name].__file__
			self.mtimes[name] = (
				moduleFile, os.stat(moduleFile).st_mtime)

	def __call__(self, environ, start_response):
		for name, (path, mtime) in self.mtimes.iteritems():
			if os.stat(path).st_mtime == mtime : continue
			print 'Reloading', name, path
			execfile(path, sys.modules[name].__dict__)
			self.mtimes[name] = path, os.stat(path).st_mtime

		return self.app(environ, start_response)

class Service :
	def __init__(self, modules=None) :
		if modules is not None :
			self._modules = modules

	def wrapper(aWrapper) :
		"""This decorator simplifies the definition of
		wrapper functions to be cascaded. The decorators 
		receive the wrapped function as second argument."""
		def decorator(wrapped) :
			def inner(self, *args, **kwd) :
				return aWrapper(self, wrapped, *args, **kwd)
			return inner
		return decorator

	@wrapper
	def _webobWrap(self, f, environ, start_response) :
		"""This decorator takes a webob based application, receiving
		a webob.Request and returning an webob.Response, into a wsgi
		compatible call method. 
		"""
		request = webob.Request(environ)
		# Untested
		if request.charset is None:
			request.charset = 'utf8'
		response = f(self,request)
		return response(environ, start_response)

	@wrapper
	def _handleErrors(self, f, request) :
		"""This decorator wraps a webob app and turns any raised
		exception into proper a HTTP error response.
		"""
		try :
			return f(self,request)
		except HttpError as e :
			return webob.Response(
				"%s: %s\n"%(e.__class__.__name__, e.message),
				status = e.status,
				content_type ='text/plain',
				)
		except Exception as e :
			return webob.Response(
				"%s: %s\n"%(e.__class__.__name__, e),
				status = "500 Internal Server Error",
				content_type = 'text/plain',
				)
		return "Should never happen"

	# TODO: Not unittested
	@wrapper
	def _handleAffero(self, f, request, module=None) :
		"""This decorator helps to acomplish the affero licence
		this code is licenced under, by providing a service 'affero'
		to get the source.
		"""
		nextLevel = request.path_info_peek()
		if nextLevel == "affero" :
			source = __file__ if module is None else module.__file__
			if source.endswith("pyc") :
				source = source[:-1]
			return webob.Response(
				file(source).read(),
				content_disposition = 'filename="%s"'%(
					os.path.basename(source)),
				content_type = 'text/plain',
				)
		if module is None : return f(self,request)
		return f(self,request, module)

	@wrapper
	def _chooseModule(self, f, request) :
		"""This wrapper consumes one path level of the request
		and checks that it matches the name of one of the
		published modules.
		"""
		moduleName = request.path_info_pop()

		if moduleName not in self._modules :
			raise NotFound("Bad service %s"%moduleName)

		module = __import__(moduleName)

		return f(self, request, module)

	@wrapper
	def _chooseTarget(self, f, request, module) :
		"""This wrapper consume one path level from the request
		and ensures that it matches a valid element within
		the module.
		"""
		moduleName = module.__name__
		targetName = request.path_info_pop()

		if not targetName :
			raise BadRequest("Specify a subservice within '%s'"%(
				moduleName))

		if targetName.startswith("_") :
			raise Forbidden("Private object")

		if targetName not in module.__dict__ :
			raise NotFound("Bad function %s.%s"%(
				moduleName, targetName))

		target = module.__dict__[targetName]

		if target.__class__.__name__ == 'module' :
			raise NotFound("Bad function %s.%s"%(
				moduleName, targetName))

		return f(self, request, target=target)

	@wrapper
	def _handleData(self, f, request, target) :
		"""
		If the target is not callable is just plain data like:
			version = "4.2"
		Just turns it into a string.
		"""
		if callable(target) : return f(self, request, target)

		return webob.Response(
			str(target),
			content_type = 'text/plain',
			)

	@_webobWrap
	@_handleErrors
	@_handleAffero
	@_chooseModule
	@_handleAffero
	@_chooseTarget
	@_handleData
	def __call__(self, request, target):
		""" Handle request """
		# TODO: Multiple valued
		requestVar = "request"
		paramnames = target.func_code.co_varnames
		hasRequest = requestVar in paramnames and paramnames.index(requestVar)==0
		nDefaults = len(target.func_defaults or ())
		nDeclared = target.func_code.co_argcount
		required = paramnames[1 if hasRequest else 0:nDeclared-nDefaults]
		declared = paramnames[:nDeclared]
		hasKeyword = target.func_code.co_flags & 0x08
		missing = [
			p for p in required
			if p not in request.params
			]
		if missing :
			raise BadRequest("Missing parameters: %s"%(
				", ".join(missing)))
		exceed = [
			p for p in request.params
			if p not in declared 
			]
		if hasRequest and requestVar in request.params :
			raise BadRequest("Unavailable parameter: %s"%requestVar)
		if exceed and not hasKeyword:
			raise BadRequest("Unavailable parameter: %s"%(
				", ".join(exceed)))

		if hasRequest :
			result = target(request=request, **request.params)
		else :
			result = target(**request.params)

		if result is None :
			return webob.Response("Done",
				content_type = getattr(
					target, 'content_type', 'text/plain'))

		if isinstance(result, basestring) :
				content_type = getattr(target, 'content_type', 'text/plain')
				return webob.Response(
					result,
					content_type = content_type,
					)

		# TODO: result being anything not a string or a Response!!

		return result



if __name__=="__main__" :
	services = sys.argv[1:] or ["TestingService"]
	application = Reload(Service(services))

	print "Loading server"
	from wsgiref.simple_server import make_server
	httpd = make_server(
		'localhost', # Host name.
		8051, # port
		application, # application object
		)
	httpd.serve_forever()


