TestFarm
========

What is it?
-----------

TestFarm is a continuous integration platform.
Several distributed TestFarm clients periodically monitor
the version control system (VCS) for updates.
Whenever an update is detected, the client starts an execution
and its results are reported to the centralized server.
Then, the server collects such reports to rebuild the web site information.

Features
--------

**TestFarm is suited for projects of volunteer developers
so that they can use their own computers as clients.**
	* Clients do not need to have an fixed IP to be reached, or be connected 24/7.
	* Clients can control the pace of VCS checks,
	  disable executions at will or
	  explicitly start an execution even with no pending updates.

* **Client executions are defined in Python.**
	* Python is a very flexible and easy language
	* It provides ways of extending the basic features

* **Supported version control systems:** Git and SVN. Extendible via plug-ins.

* The generated website is pure HTML + CSS + JavaScript pages.
  No server side PHP or Python is needed to visualize it.
  Server side Python is used to collect and update the website.
* Collects stats such as SLOC, number of tests... and
  present them in a time graph.

Status
------

After many years with version 1, TestFarm has been rewritten
on the server side to make it more scalable and mantainable.



This documentation is WIP.

More info at [this blog][here].

[here]: http://canvoki.net/coder/blog/2013-03-21-refactoring-the-testfarm-server.html




