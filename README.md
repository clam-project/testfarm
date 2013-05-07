TestFarm
========

What is it?
-----------

TestFarm is a continuous integration platform.
The typical workflow is:
* Several clients monitor periodially for updates
  at the project version control system (VCS).
* When a client detects any update, it starts an execution.
* As execution goes on, progress and results are reported to the TestFarm server.
* The server collects such data to build a public web site.
* Developers can consult that web site to see whether
  their changes had unexpected impacts over other platforms or configurations.

![TestFarm Summary](http://canvoki.net/coder/media/images/testfarmserver2-summarypage.png)


Features
--------

* **TestFarm is suited for projects of volunteer developers
  so that they can use their own computers as clients.**
	* Clients do not need to have fixed IP to be reached.
	* Clients do not need to be connected 24/7.
	* Clients can control the pace of VCS checks.
	* Clients can disable executions at will.
	* Clients can explicitly start an execution even with no pending updates.
	* Clients can report to a local logger when internet goes down.
* **Client are defined as Python scripts.**
	* Tasks are sequences of shell commands wrapped with Python code.
	* Python provides flexibility and expressiveness.
	* Commands can be parametrized by configuration parameters using templates
	* Off-the-shelf TestFarm features can be extended in the same client script.
* **Minimum requirements.**
	* The generated public website is pure HTML + CSS + JavaScript pages.
	* No server side PHP or Python is needed to visualize it.
	* Server side Python scripts are used to collect remote client data. WSGI (recommended) or FastCGI.
	* No database is required, it uses file based logs.
	* It just depends on pure Python dependencies that can be installed in a virtualenv.
* **Version Control Systems.**
	* A client can monitor several repositories at once
	* Supported VCS's: Subversion, Git
	* Extendible to other VCS's via plug-ins
* **Notifications.**
	* Mail notifications
	* IRC notifications
	* Tray icon applet
	* API to add custom notification methods
	* JSON access to the current status
* **Stats: Collecting time evolving numerical data.**
	* Numerical data can be collected from the executed commands
	* Presented at the web site as time plots.
	* Some provided off-the-shelf: SLOC, number of tests...
	* You can define your custom ones.

Status
------

After many years with version 1, TestFarm has been rewritten
on the server side to make it more scalable and mantainable.
The client API still remains close to v1 but we want to rewrite 
it too to simplify and clearify clients scripts.

Anyway you can use v1 client API with no fear as we plan to offer
a compatibility layer similar to the one we are offering now.

More info about the server rewrite at [this blog][here].

[here]: http://canvoki.net/coder/blog/2013-03-21-refactoring-the-testfarm-server.html


TO DOCUMENT
-----------

This documentation is WIP.



