#! /usr/bin/python
from testfarmserver import TestFarmServer

def main():
	server = TestFarmServer(
		logs_base_dir = '/tmp/remote_testfarm_logs/',
		html_dir = '/tmp/remote_testfarm_html/'
	)
	server.update_static_html_files()
		

if __name__ == '__main__':
	main()
