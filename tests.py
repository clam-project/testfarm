#! /usr/bin/python
import unittest
from testfarmclient import *
from test_task import Tests_Task
from test_repository import Tests_Repository
from test_testfarmclient import Tests_TestFarmClient
from test_testfarmserver import Tests_TestFarmServer, Tests_ServerListener	

def main():
	unittest.main()

if __name__ == '__main__':
	main()

