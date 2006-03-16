#! /usr/bin/python

from testfarmclient import Repository, TestFarmClient

clam = Repository("CLAM")
clam.add_deployment_task( [
	"echo lalala",
	"ls" 
] )
clam.add_task("teeesting", [
	"./lalala fafaf",
	"echo Should not write this!"
] )
clam.add_task("another", [
	"echo Do should write this!"
] )
#[tal] 244.3
#[total num cycles] 233


TestFarmClient( [
	clam
] )
