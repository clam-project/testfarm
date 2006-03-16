#! /usr/bin/python
import unittest
from testfarm import *
from test_task import Tests_Task
from test_repository import Tests_Repository
from test_testfarmclient import Tests_TestsFarmClient
from test_testfarmserver import Tests_TestsFarmServer, Tests_ServerListener	

def main():
	unittest.main()

if __name__ == '__main__':
	main()

