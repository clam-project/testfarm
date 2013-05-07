TestFarm
========

What is it?
-----------

TestFarm is a continuous integration platform.
The typical workflow is:
* Several clients,
  usually running on different platforms/configurations,
  monitor periodically for updates
  at the project version control system (VCS).
* When a client detects any changes, it starts an execution.
* Execution progress and results are reported to the TestFarm server.
* The server collects such data into a public web site.
* Developers can take a look at that web site to see whether
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
	* No database is required, it relies on file based logs.
	* It just depends on pure Python dependencies that can be installed on a virtualenv.
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

Project status
--------------

After many years with version 1, TestFarm has been rewritten
on the server side to make it more scalable and mantainable.
The client API still remains close to v1 but we want to rewrite 
it too to simplify and clearify client scripts.

Anyway you can use v1 client API with no fear as we plan to offer
a compatibility layer similar to the one we are offering now.

More info about the server rewrite at [this blog][here].

[here]: http://canvoki.net/coder/blog/2013-03-21-refactoring-the-testfarm-server.html


TO DOCUMENT
-----------

This documentation is WIP.
Meanwhile you can take a look at the `client_selftest.py` example.

- Invoking a client
- Client definition
	- Defining a client
	- Defining the repositories
	- Configuration and commands parametrization
	- Setting up a local logger
	- Reporting to a remote logger
	- Collecting stats
	- Defining custom stats
	- Overriding command status and output
- Extending TestFarm
	- Adding a new VCS system
	- Adding a new notification method
	- Using JSON data
- Server configuration
	- Apache + WSGI
	- Apache + FastCGI + Flup
	- Using VirtualEnv


Screenshots
-----------


### Project Summary Page

Provides a quick overview of the status of all the clients.

![TestFarm Summary](http://canvoki.net/coder/media/images/testfarmserver2-summarypage.png)

### Project History Page

Shows all the executions along the time of the clients of a project.

![TestFarm Summary](http://canvoki.net/coder/media/images/testfarmserver2-historypage.png)

### Execution Details Page

Shows the details of an execution, tasks, commands...
with the output of the failed commands and the extracted info and stats.

![TestFarm Execution Details](http://canvoki.net/coder/media/images/testfarmserver2-detailspage.png)

### Client Stats Page

By clicking on the thumbnail we get a bigger time plot with all the collected client stats.

![TestFarm Execution Details](http://canvoki.net/coder/media/images/testfarmserver2-clientstats.png)

### TestFarm Indicator

The TestFarm Indicator is a tray icon applet. Whenever a client is broken, it warns you by burning the farm.

![TestFarm Execution Details](http://canvoki.net/coder/media/images/testfarm-indicator-balloon.png)





