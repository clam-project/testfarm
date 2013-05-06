#!/usr/bin/python

import urllib, urllib2
import urlparse
import HttpFormPost
import sys
import decorator
from functools import wraps
import inspect

def remote(f) :
	@wraps(f)
	def wrapper(self, *args, **kwds) :
		f(self, *args, **kwds) # This just checks the signature
		kwds.update(dict((
			(name, arg)
			for arg, name
			in zip(args, inspect.getargspec(f).args[1:])
			)))
		return self.callRemotely(f.__name__, **kwds)
	return wrapper

class RemoteError(Exception) :
	pass
	
class ServiceProxy(object) :
	def __init__(self, baseUrl) :
		self.baseUrl = baseUrl

		"""
		# Untested proxy code, used to work before refactoring
		# but it was quite adhoc for our situation and now...
		Proxies = dict(
			http = http://proxy.upf.edu:8080',
			ftp = 'http://proxy.upf.edu:8080',
		}
		NoProxiesFor = [
			"localhost",
			"127.0.0.1",
			"10.55.0.40",
		]

		if urlparse.urlparse (self.serviceUrl)[1] in NoProxiesFor :
			self.proxies={}
		self.proxies = {}
		proxy_support = urllib2.ProxyHandler( self.proxies )
		opener = urllib2.build_opener( proxy_support )
		urllib2.install_opener(opener)
		"""

	def callRemotely(self, serviceName, **fields) :
		fields = dict(((k,repr(v)) for k,v in fields.iteritems()))
		content_type, body = HttpFormPost.encode_multipart_formdata_dictionary(fields)
		headers = {
			'Content-Type': content_type,
			'User-Agent': 'python-service-proxy/1.0',
		}
		req=urllib2.Request(
			self.baseUrl+"/"+serviceName, body, headers)
		try :
			result = urllib2.urlopen(req).read()
		except urllib2.HTTPError as e :
			if e.getcode() == 500 :
				message = e.read()
				raise RemoteError(message)
			raise
		return result







if __name__ == "__main__" :
	webservice = ServiceStub("http://localhost:8051/ContentLocator")
	print webservice.remoteCall("Version")
	print webservice.remoteCall("LocateId", id="4871335")
	print webservice.remoteCall("LocateId", id=["4871335","lala"])
	print webservice.remoteCall("_private")
#	print webservice.remoteCall("LocateId", id=open(__file__,'rb'))
#	print webservice.remoteCall("LocateId", id=open("/home/vokimon/0002.jpg",'rb'))
	

