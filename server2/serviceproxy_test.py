#!/usr/bin/python

import wsgi_intercept.urllib2_intercept
import unittest
import urllib2
import HttpFormPost
import os
from serviceproxy import ServiceProxy
import webob

class ServiceProxyTest(unittest.TestCase) :
	def setUp(self) :
		self.maxDiff = None
		def createApp() :
			def appStub(request, start_response) :
				self.query = webob.Request(request)
				if "error" in self.query.params :
					message = self.query.params['error']
					start_response("500 Internal Server Error", [])
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
		self.assertEqual(self.query.params,dict(a='boo'))

	def test_callRemotely_withArgs(self) :
		p = ServiceProxy("http://myhost:80")
		p.callRemotely("service", a="boo", b="foo")

		self.assertEqual(self.query.path,'/service')
		self.assertEqual(self.query.params,dict(a='boo', b='foo'))

	def test_callRemotely_returnsText(self) :
		p = ServiceProxy("http://myhost:80")
		result = p.callRemotely("service")
		self.assertEqual(result, "Hola")

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



if __name__=="__main__" :
	unittest.main()


