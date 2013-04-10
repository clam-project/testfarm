"""
Copyright 2013 David Garcia Garzon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import inspect

class NullReporter(object) :

	def idle(self, minutes, running=False) : pass
	def startExecution(self, execution) : pass
	def startTask(self, execution, task, description) : pass
	def startCommand(self, execution, task, command, commandline) : pass
	def stopCommand(self, execution, task, command,
			output, ok, info, stats,
			) : pass
	def stopTask(self, execution, task, ok) : pass
	def stopExecution(self, execution) : pass


class LogWrapper(object) :
	class wrapper(object) :
		def __init__(self, wrapped, method) :
			self.wrapped = wrapped
			self.method = method
		def __call__(self, *args, **kwds) :
			return self.wrapped._loggedCall(self.method, *args, **kwds)

	def __init__(self, wrapped) :
		self._wrapped = wrapped
		self._calls = []

	def calls(self) :
		return self._calls

	def __getattr__(self, method ) :
		"Whenever you access an non-existing attribute or method"
		return LogWrapper.wrapper(self, method)

	def _loggedCall(self, method, *args, **kwds) :
		f = getattr(self._wrapped, method)
		fdef = inspect.getargspec(f)
		fargs = fdef.args[1:] # removing 'self'
		if len(fargs) < len(args) :
			raise TypeError(
				"{f.__name__} expected at most {expected} arguments, got {got}"
				.format(expected=len(fargs)+1, got=len(args)+1,**vars()))
		repeatedKeys = [
			key
			for key in fargs[:len(args)]
			if key in kwds
			]
		if repeatedKeys :
			raise TypeError(
				"{f.__name__}() got multiple values "
				"for keyword argument '{repeatedKeys[0]}'"
				.format(**vars()))

		kwds.update({
			key : value
			for key, value
			in zip(fargs, args)
			}) 
		params = {
			key : value
			for key, value
			in zip(fargs[-len(fdef.defaults):], fdef.defaults)
			} if fdef.defaults else {}
		params.update(**kwds)
		self._calls.append( (
			f.__name__, params))
		return f(**kwds)


def MockUpReporter() :
	return LogWrapper(NullReporter())

class MultiReporter(object) :
	"Forwards method calls to a set of added objects"

	class wrapper(object) :
		def __init__(self, wrapped, method) :
			self.wrapped = wrapped
			self.method = method
		def __call__(self, *args, **keyw) :
			self.wrapped._multicall(self.method, *args, **keyw)

	def __init__(self, subs=[]) :
		self._added = subs[:]

	def add(self, sub) :
		self._added.append(sub)

	def __getattr__(self, method ) :
		"Whenever you access an non-existing attribute or method"
		return MultiReporter.wrapper(self, method)

	def _multicall(self, method, *args, **keyw) :
		"Not to be called directly"
		return [ 
			getattr(sub,method) (*args, **keyw)
			for sub in self._added
		]


