CHANGE LOG
==========

????-??-?? TestFarm 2.1
-----------------------

* index.html is the summary page.

2013-05-07 TestFarm 2.0
-----------------------

* Server rewrite
	* Rewritten using Test Driven Development
	* Encapsulated log access, so that log structure is 
	  an internal implementation detail of a single class.
	* Simple access to log information using attribute maps.
	* Logs splitted by project/client/execution.
	* Logs organized in directories for faster access.
	* Cheap information have their own access point.
* Wrapper for v1 clients attached to v2 loggers
* Simplified and configurable IRC reporter
* Configurable Mail reporter
* Tray icon applet to monitor TestFarm status
* Easy install (pip install testfarm)
* Command line tool (testfarmserver) to setup and control a testfarm log
* Easy server deployment
	* WSGI method (recommended)
	* FastCGI method (for hostings with restrictions like DreamHost)

	

