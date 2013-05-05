#!/usr/bin/python

import wsgi_intercept.urllib2_intercept
import unittest
import urllib2
import HttpFormPost
import os
from serviceproxy import ServiceProxy
from serviceproxy import RemoteError
from serviceproxy import remote
import webob
import ast

class ServiceProxyTest(unittest.TestCase) :
	def setUp(self) :
		self.maxDiff = None
		def createApp() :
			def appStub(request, start_response) :
				self.query = webob.Request(request)
				self.params = dict((
					(k,ast.literal_eval(v))
					for k,v in self.query.params.items()
					))
				if "error" in self.params :
					message = self.params['error']
					start_response("500 Internal Server Error", [])
					return message
				if "notfound" in self.params :
					message = self.params['notfound']
					start_response("404 Not found", [])
					return message
				return "Hola"
			return appStub
		wsgi_intercept.urllib2_intercept.install_opener()
		wsgi_intercept.add_wsgi_intercept('myhost', 80, createApp)


	def tearDown(self) :
		wsgi_intercept.urllib2_intercept.uninstall_opener()

	def test_callRemotely_noArgs(self) :
		p = ServiceProxy("http://myhost:80")
		p.callRemotely("service")

		self.assertEqual(self.query.path,'/service')
		self.assertEqual(self.query.method,'POST')
		self.assertEqual(self.query.params,{})

	def test_callRemotely_anouncesAsUserAgent(self) :
		p = ServiceProxy("http://myhost:80")
		p.callRemotely("service")

		self.assertEqual(self.query.user_agent,
			"python-service-proxy/1.0")

	def test_callRemotely_withArg(self) :
		p = ServiceProxy("http://myhost:80")
		p.callRemotely("service", a="boo")

		self.assertEqual(self.query.path,'/service')
		self.assertEqual(self.query.method,'POST')
		self.assertEqual(self.params,dict(a='boo'))

	def test_callRemotely_withArgs(self) :
		p = ServiceProxy("http://myhost:80")
		p.callRemotely("service", a="boo", b="foo")

		self.assertEqual(self.query.path,'/service')
		self.assertEqual(self.params,dict(a='boo', b='foo'))

	def test_callRemotely_returnsText(self) :
		p = ServiceProxy("http://myhost:80")
		result = p.callRemotely("service")
		self.assertEqual(result, "Hola")

	def test_callRemotely_withIntArgs(self) :
		p = ServiceProxy("http://myhost:80")
		p.callRemotely("service", a=1)

		self.assertEqual(self.query.path,'/service')
		self.assertEqual(self.params,dict(a=1))

	def test_callRemotely_badHost(self) :
		p = ServiceProxy("http://badhost:80")
		try :
			p.callRemotely("service")
			self.fail("Exception expected")
		except urllib2.URLError as e :
			self.assertEqual(e.message, "")

	def test_callRemotely_internalError(self) :
		p = ServiceProxy("http://myhost:80")
		try :
			p.callRemotely("service", error="Message")
			self.fail("Exception expected")
		except urllib2.HTTPError as e :
			self.assertEqual(e.reason, "Internal Server Error")
			self.assertEqual(e.read(), "Message")
			self.assertEqual(e.getcode(), 500)

	def test_callRemotely_notFoundError(self) :
		p = ServiceProxy("http://myhost")
		try :
			p.callRemotely("service", notfound="Message")
			self.fail("Exception expected")
		except urllib2.HTTPError as e :
			self.assertEqual(e.reason, "Not found")
			self.assertEqual(e.read(), "Message")
			self.assertEqual(e.getcode(), 404)

	def test_callRemotely_internalError(self) :
		p = ServiceProxy("http://myhost:80")
		try :
			p.callRemotely("service", error="Message")
			self.fail("Exception expected")
		except RemoteError as e :
			self.assertEqual(e.message, "Message")

	# TODO Remote errors providing more information

	class MyModel(ServiceProxy) :
		def __init__(self, url) :
			super(ServiceProxyTest.MyModel,self).__init__(url)
		@remote
		def callme(self, a, b) : pass
		
	def test_remoteDecorator(self) :
		p = ServiceProxyTest.MyModel("http://myhost:80")

		p.callme(a="boo", b="foo")

		self.assertEqual(self.query.path,'/callme')
		self.assertEqual(self.params,dict(a='boo', b='foo'))

	def test_remoteDecorator_wrongParams(self) :
		p = ServiceProxyTest.MyModel("http://myhost:80")
		try :
			p.callme(a="boo", c="foo")
			self.fail("exception expected")
		except TypeError as e :
			self.assertEqual(e.message,
				"callme() got an unexpected keyword argument 'c'")


if __name__=="__main__" :
	unittest.main()


