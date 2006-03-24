#! /usr/bin/python
import urllib 
import urlparse

Proxies = { 'http' : 'http://proxy.upf.edu:8080', 'ftp' : 'http://proxy.upf.edu:8080' }
NoProxiesFor = ["localhost", "127.0.0.1", "10.55.0.50", "10.55.0.66"]
useragent = 'simac-annotator-tasker'


class ServiceProxy :
	def __init__(self, serviceLocation, proxies=Proxies) :
		self.serviceUrl = serviceLocation
		self.proxies = proxies
		pass

	def remote_call(self, serviceName, **kwargs) :
		params=urllib.urlencode(kwargs)
		if urlparse.urlparse ( self.serviceUrl )[1] in NoProxiesFor :
			serviceResult=urllib.urlopen(self.serviceUrl+"/"+serviceName, params, {}).read();
		else :
			serviceResult=urllib.urlopen(self.serviceUrl+"/"+serviceName, params, Proxies).read();
		return serviceResult


class ContentLocator(ServiceProxy) :
	def LocateId(self, id) :
		return self.remote_call( "LocateId", id=id )

	def IdentifyUrl(self, url) :
		return self.remote_call( "IdentifyUrl", url=url )

	def AddUrl(self, url) :
		return self.remote_call( "AddUrl", url=url )


class MetadataProvider(ServiceProxy) :
	def QueryIdByUrl(self, url) :
		return self.remote_call( "QueryIdByUrl", url=url )

	def QuerySchema(self, descriptors) :
		return self.remote_call( "QuerySchema", descriptors=descriptors )

	def QueryDescriptors(self, id, descriptors) :
		return self.remote_call( "QueryDescriptors", id=id, descriptors=descriptors)

	def UploadPackedDescriptors(self, file) :
		return self.remote_call( "UploadPackedDescriptors", packedpoolfile=open(file, 'rb') )

	def AvailableDescriptors(self) :
		return self.remote_call("AvailableDescriptors")

def main() :
	webservice = ServiceProxy("http://localhost/testfarm_server")
	print webservice.remote_call("a_method", text="some")
	return 

if __name__ == "__main__" :
	main()
