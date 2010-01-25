#
#  Copyright (c) 2006 Pau Arumi, Bram de Jong, Mohamed Sordo 
#  and Universitat Pompeu Fabra
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#

import urllib 
import urlparse

Proxies = { } #'http' : 'http://proxy.upf.edu:8080', 'ftp' : 'http://proxy.upf.edu:8080' }
NoProxiesFor = [
	"localhost",
	"127.0.0.1",
	"10.55.0.50",
	"10.55.0.66",
	"efpc072.upf.es",
	"ocata48123.upf.es",
]
useragent = 'testfarm-python-client'


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
