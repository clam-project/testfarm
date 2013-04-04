import httplib, mimetypes

"""
Functions related to data posting as if it were created from an HTML form.
Files can be managed correctly.

Found there:
   "Http client to POST using multipart/form-data"
   http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
 -(Added wrapper to work with a dictionary)
"""


def encode_multipart_formdata(fields, files):
	"""
	fields is a sequence of (name, value) elements for regular form fields.
	files is a sequence of (name, filename, value) elements for data to be uploaded as files
	Return (content_type, body) ready for httplib.HTTP instance
	"""
	BOUNDARY = '----------Nobody-expects-the-Spanish-Inquisition'
	CRLF = '\r\n'
	L = []
	for (key, value) in fields:
		L.append('--' + BOUNDARY)
		L.append('Content-Disposition: form-data; name="%s"' % key)
		L.append('')
		L.append(value)
	for (key, filename, value) in files:
		L.append('--' + BOUNDARY)
		L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
		L.append('Content-Type: %s' % get_content_type(filename))
		L.append('')
		L.append(value)
	L.append('--' + BOUNDARY + '--')
	L.append('')
	body = CRLF.join(L)
	content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
	return content_type, body


def get_content_type(filename):
	return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def post_multipart(host, selector, useragent, fields, files):
	"""
	Post fields and files to an http host as multipart/form-data.
	fields is a sequence of (name, value) elements for regular form fields.
	files is a sequence of (name, filename, value) elements for data to be uploaded as files
	Return the server's response page.
	"""
	content_type, body = encode_multipart_formdata(fields, files)
	h = httplib.HTTPConnection(host)  
	headers = {
		'User-Agent': useragent,
		'Content-Type': content_type
		}
	h.request('POST', selector, body, headers)
	res = h.getresponse()
	return res.read()


def encode_multipart_formdata_dictionary( params):
	fields=[]
	files=[]

	for key in params.keys():
		t=str( type( params[key] ) )

		if t=="<type 'list'>":
			for item in params[key]:
				fields.append( (key,item) )
		elif t=="<type 'file'>":
			files.append( (key,'dummyname.file',params[key].read() ) )
		else:
			fields.append( (key,params[key]) )

	return encode_multipart_formdata(fields, files)


if __name__ == "__main__":
	print post_multipart("localhost","/SimacServices/kk.py/Upload", 'simac-annotator-tasker', [], [('data','upload.xml', open('uploadfile.xml.gz','rb').read() )])
