#! /usr/bin/python

from testfarmclient import Repository, TestFarmClient

for_loop = Repository("slow test")

for_loop.add_task("echo", ["echo hello"] )
for_loop.add_task("sleep 5 i 20 seconds", ["sleep 5", "sleep 20"] )
for_loop.add_task("sleep 3 i 12 seconds", ["sleep 3", "sleep 12"] )



TestFarmClient( "msordo_linux_breezy", [for_loop], generated_html_path = "html2" )
