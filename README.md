TestFarm
========

What is it?
-----------

TestFarm is a continuous integration platform.
The typical workflow is:
* Several clients monitor periodially for updates
  at the project version control system (VCS).
* When a client detects any update,
  it starts an execution and
  reports the results to the TestFarm server.
* The server collects this data to build a public web,
* Developers can see whether 
  their changes had unexpected impacts over other platforms or configuration.

![TestFarm Summary](http://canvoki.net/coder/media/images/testfarmserver2-summarypage.png)


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




