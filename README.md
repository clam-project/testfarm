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
	* Clients do not need to have an fixed IP to be reached.
	* Clients do not need to be connected 24/7.
	* Clients can control the pace of VCS checks.
	* Clients can disable executions at will.
	* Clients can explicitly start an execution even with no pending updates.
	* Clients can report to a local logger when internet goes down.
* **Client executions are defined in Python.**
	* Tasks are sequences of shell commands wrapped in Python code.
	* Python provides syntactic sugar and expressiveness to the client definition.
	* Python provides ways of extending the off-the-shelf TestFarm features.
* **Version Control Systems.**
	* A client can monitor several repositories at once
	* Supported: Subversion, Git
	* Extendible to other VCS's via plug-ins
* **Minimum requirements.**
	* The generated public website is pure HTML + CSS + JavaScript pages.
	  No server side PHP or Python is needed to visualize it.
	* Server side Python (wsgi or fastcgi) is used to collect and update the website.
	* No database is required, it uses file based logs
* **Collecting time evolving numerical data.**
	* Numerical data can be collected from the executed commands
	* Presented at the web site as time plots.
	* Some provided: SLOC, number of tests...
	* You can define your custom ones.

Status
------

After many years with version 1, TestFarm has been rewritten
on the server side to make it more scalable and mantainable.



This documentation is WIP.

More info at [this blog][here].

[here]: http://canvoki.net/coder/blog/2013-03-21-refactoring-the-testfarm-server.html




