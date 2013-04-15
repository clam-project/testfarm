#!/usr/bin/python

_serviceCode = """\
#!/usr/bin/python

import sys # not used, just to try to call it

Protocol="TestingProtocol"
_private = "Private content"
Numeric = 13

def Function0() :
	return "Function0 content"

def Function0_html() :
	return "Function0_html <b>content</b>"
Function0_html.content_type = 'text/html'

def ErrorFunction() :
	return [][0]

def Function1(param1) :
	return "param1 = %s"%param1

def Function1Optional(param1="defaultValue") :
	return "param1 = %s"%param1

def FunctionKeyword(**kwd) :
	return str(kwd)

def FunctionPositional(a, *b) :
	return "a = '%s'\\nargs = %s"%(a,b)

def FunctionRequest(request, a, b) :
	return request.method

def FunctionRequestKeyword(request, **kwd) :
	return request.method

def FunctionReturningResponse(request) :
	import webob
	return webob.Response("Content",
		content_type='text/plain',
		)

def FunctionReturningNone() :
	return None

def dummySigner(signature, id, **kwd) :
	from testfarm import service
	keys = dict(
		alibaba="sesame, open",
		)
	if id not in keys : raise service.Forbidden("Not such id")
	expectedKey = keys[id]+'0' #str(len(kwd))
	if signature != expectedKey : raise service.Forbidden("Bad signature")

from testfarm import paramexpander
@paramexpander.expandfunction(dummySigner)
def signedFunction0() :
	return "Ok"

"""

import wsgi_intercept.urllib2_intercept
import unittest
import urllib2
import HttpFormPost
import os
import sys

class ServiceTest(unittest.TestCase) :

	def setUp(self) :
		source = open("TestingService.py",'w')
		source.write(_serviceCode)
		source.close()
		del source
		import service
		self.app = service.Reload(service.Service([
			"TestingService",
			]))
		def createApp() : return self.app
		wsgi_intercept.urllib2_intercept.install_opener()
		wsgi_intercept.add_wsgi_intercept('myhost', 80, createApp)
		sys.path.append(os.getcwd())


	def tearDown(self) :
		wsgi_intercept.urllib2_intercept.uninstall_opener()
		os.unlink("TestingService.py")
		if os.path.exists("TestingService.pyc") :
			os.unlink("TestingService.pyc")
		sys.path.remove(os.getcwd())

	def request(self, query, postdata=None) :
		body = None
		headers = {}
		if postdata is not None :
			content_type, body = HttpFormPost.encode_multipart_formdata_dictionary(postdata)
			headers['Content-Type'] = content_type
		req=urllib2.Request('http://myhost:80/'+query, body, headers)
		return urllib2.urlopen(req)

	def assertContent(self, query, body=None, headers=None, post=None) :
		try :
			req = self.request(query, post)
			requestBody = req.read()
			if body is not None :
				self.assertEquals(body, requestBody)
			if headers is not None :
				headers = headers.format(bodysize=len(requestBody))
				self.assertEquals(headers, str(req.headers))
		except urllib2.HTTPError as e :
			print (e.read())
			raise

	def assertError(self, query, code, body=None, headers=None, post=None) :
		try :
			res = self.request(query, post)
			self.fail("HTTP error expected. Received '%s'"%res.read())
		except urllib2.HTTPError as e :
			requestBody = e.read()
			if body is not None :
				self.assertEquals(body, requestBody)
			self.assertEquals(code, e.getcode())
			if headers is not None:
				headers = headers.format(bodysize=len(requestBody))
				self.assertEquals(headers, str(e.headers))

	def headerHtmlText(self) :
		return (
			"""Content-Type: text/html; charset=UTF-8\n"""
			"""Content-Length: {bodysize}\n"""
			)

	def headerPlainText(self) :
		return (
			"""Content-Type: text/plain; charset=UTF-8\n"""
			"""Content-Length: {bodysize}\n"""
			)

	def testMissingModule(self) :
		self.assertError(
			'BadModule/Protocol',
			code = 404,
			body = "NotFound: Bad service BadModule\n",
			headers = self.headerPlainText(),
			)

	def testMissingTarget(self) :
		self.assertError(
			'TestingService/MissingTarget',
			code = 404,
			body = "NotFound: Bad function TestingService.MissingTarget\n",
			headers = self.headerPlainText(),
			)

	def testGetAttributes(self) :
		self.assertContent(
			'TestingService/Protocol',
			body="TestingProtocol",
			)

	def testGetAttributes_defaultsToPlainText(self) :
		self.assertContent(
			'TestingService/Protocol',
			headers = self.headerPlainText(),
			)

	def testPrivateObject(self) :
		self.assertError(
			'TestingService/_private',
			code = 403,
			body = "Forbidden: Private object\n",
			headers = self.headerPlainText(),
			)

	def testNumericAttribute(self) :
		self.assertContent(
			"TestingService/Numeric",
			'13')

	def testModule_failsNotFound(self) :
		self.assertError(
			'TestingService/sys',
			code = 404,
			body = "NotFound: Bad function TestingService.sys\n",
			headers = self.headerPlainText(),
			)

	def testFunction0_html(self) :
		self.assertContent(
			"TestingService/Function0_html",
			'Function0_html <b>content</b>',
			headers = self.headerHtmlText(),
			)

	def testErrorFunction0_html(self) :
		self.assertError(
			"TestingService/ErrorFunction",
			500,
			'IndexError: list index out of range\n',
			)

	def testFunction1_withNoParams(self) :
		self.assertError(
			"TestingService/Function1",
			400,
			'BadRequest: Missing parameters: param1\n',
			headers = self.headerPlainText(),
			)

	def testFunction1_usingGet(self) :
		self.assertContent(
			"TestingService/Function1?param1=value1",
			body = 'param1 = value1',
			headers = self.headerPlainText(),
			)

	def testFunction1_usingMultipleGet_lastWins(self) :
		self.assertContent(
			"TestingService/Function1?param1=value1&param1=value2",
			body = 'param1 = value2',
			headers = self.headerPlainText(),
			)

	def testFunction1_usingPost(self) :
		self.assertContent(
			"TestingService/Function1",
			post = dict(param1='post value'),
			body = 'param1 = post value',
			headers = self.headerPlainText(),
			)

	def testFunction1_usingPostAndUri_getWins(self) :
		self.assertContent(
			"TestingService/Function1?param1=get",
			post = dict(param1='post'),
			body = 'param1 = get',
			headers = self.headerPlainText(),
			)

	def testFunction0_withParams(self) :
		self.assertError(
			"TestingService/Function0?param=value",
			400,
			'BadRequest: Unavailable parameter: param\n',
			headers = self.headerPlainText(),
			)

	def testFunction1Optional_withoutTheParam(self) :
		self.assertContent(
			"TestingService/Function1Optional",
			body = 'param1 = defaultValue',
			headers = self.headerPlainText(),
			)

	def testFunctionKeyword_withoutParams(self) :
		self.assertContent(
			"TestingService/FunctionKeyword",
			body = '{}',
			headers = self.headerPlainText(),
			)

	def testFunctionKeyword_withParams(self) :
		self.assertContent(
			"TestingService/FunctionKeyword?a=1&b=2",
			body = "{u'a': u'1', u'b': u'2'}",
			headers = self.headerPlainText(),
			)

	def testFunctionPositional(self) :
		self.assertContent(
			"TestingService/FunctionPositional?a=1",
			body = "a = '1'\nargs = ()",
			headers = self.headerPlainText(),
			)

	def testFunctionPositional_withExtraParam(self) :
		self.assertError(
			"TestingService/FunctionPositional?a=1&c=2",
			code = 400,
			body = "BadRequest: Unavailable parameter: c\n",
			headers = self.headerPlainText(),
			)

	def testFunctionPositional_withExtraParamNamedLikeThePositional(self) :
		self.assertError(
			"TestingService/FunctionPositional?a=1&b=2",
			code = 400,
			body = "BadRequest: Unavailable parameter: b\n",
			headers = self.headerPlainText(),
			)

	def testFunctionRequest(self) :
		self.assertContent(
			"TestingService/FunctionRequest?a=1&b=2",
			body = "GET",
			headers = self.headerPlainText(),
			)

	def testFunctionRequest_requestHijack(self) :
		self.assertError(
			"TestingService/FunctionRequest?a=1&b=2&request='hijack'",
			400,
			body = "BadRequest: Unavailable parameter: request\n",
			headers = self.headerPlainText(),
			)

	def testFunctionRequest(self) :
		self.assertContent(
			"TestingService/FunctionRequestKeyword?a=1&b=2",
			body = "GET",
			headers = self.headerPlainText(),
			)

	def testFunctionRequestKeyword_requestHijack(self) :
		self.assertError(
			"TestingService/FunctionRequestKeyword?request='hijack'",
			400,
			body = "BadRequest: Unavailable parameter: request\n",
			headers = self.headerPlainText(),
			)

	def testReload(self) :
		import time
		script = "TestingService.py"
		self.request("TestingService/Function0").read()
		creationtime = os.stat(script).st_mtime
		while True : # mtime has just one second of resolution
			source = open(script,'w')
			source.write(
				"print 'Loading'\n"
				"def Function0() : return 'Reloaded!!'\n"
				)
			source.close()
			if os.stat(script).st_mtime != creationtime : break

		self.assertContent(
			"TestingService/Function0",
			body = "Reloaded!!",
			headers = self.headerPlainText(),
			)

	def test_noService(self) :
		self.assertError(
			"TestingService?bad=boom&good=nice",
			400,
			body = "BadRequest: Specify a subservice within 'TestingService'\n",
			headers = self.headerPlainText(),
			)

	def test_FunctionReturningResponse(self) :
		self.assertContent(
			"TestingService/FunctionReturningResponse",
			body = "Content",
			headers = self.headerPlainText(),
			)

	def test_voidFunction(self) :
		self.assertContent(
			"TestingService/FunctionReturningNone",
			body = "Done",
			headers = self.headerPlainText(),
			)


	def test_signedFunction0_withNoParameters(self) :
		self.assertError(
			"TestingService/signedFunction0",
			400,
			body = "BadRequest: Missing parameters: signature, id\n",
			headers = self.headerPlainText(),
			)

	def test_signedFunction0_withBadId(self) :
		self.assertError(
			"TestingService/signedFunction0?id=badId&signature=nevermind",
			403,
			body = "Forbidden: Not such id\n",
			headers = self.headerPlainText(),
			)

	def test_signedFunction0_withBadSignature(self) :
		self.assertError(
			"TestingService/signedFunction0?id=alibaba&signature=sesame0",
			403,
			body = "Forbidden: Bad signature\n",
			headers = self.headerPlainText(),
			)

if __name__=="__main__" :
	unittest.main()


