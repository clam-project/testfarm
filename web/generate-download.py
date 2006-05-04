#! /usr/bin/python

import glob, sys, commands

def execute(cmd):
	return commands.getstatusoutput(cmd)[1]

def write_download_page() :
	html = []
	for details in execute('ls -lht export/*.tar.gz').split('\n'):
		separated = details.split()
		if separated[2] != 'parumi' : continue 
		size = separated[4] 
		date = separated[5] 
		file = separated[7]
		shortfile = file[len('export/'):]
		print 'adding', shortfile
		html.append('<li>')
		html.append('<a href="%s">%s</a> %s  %s' % (file, shortfile, size, date) )
		html.append('</li>')

	f = open('download.html', 'w')
	f.write ( open('download.html.in').read() % '\n'.join(html) )


def create_tarball(version):
		print 'Creating tarball: testfarm-%s' % version
		cmd = 'cd export && cvs export -r HEAD -d testfarm-%(ver)s testfarm' % {'ver':version}
		print cmd
		print execute(cmd)
 		cmd = 'cd export/examples && rm songstamp* essentia*'
		print execute(cmd)
		cmd = 'cd export && tar cvf testfarm-%(ver)s.tar.gz testfarm-%(ver)s/ && rm -rf testfarm-%(ver)s/' % {'ver':version}
		print execute(cmd)


if __name__ == '__main__':
	if len( sys.argv ) == 2:
		version = sys.argv[1]
		create_tarball(version)
	else :
		print 'Version argument not detected. So will not create any tarball' 
	write_download_page()
	
	print "Do you want to upload the web? [y/n]"
	if raw_input().strip() in ['y', 'Y', 'yes']:
		cmd = 'cd .. && scp -r web/* parumi@www.iua.upf.es:pagines/testfarm/'
		print 'executing:', cmd
		execute( cmd ) 
	else :
		print 'exiting without uploading'

