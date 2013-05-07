CHANGE LOG
==========

????-??-?? TestFarm 2.1
-----------------------

* index.html is the summary page.

2013-05-07 TestFarm 2.0
-----------------------

* Server rewrite
	* Rewritten using Test Driven Development
	* Encapsulated log access, (Logger) so that log structure
	  is an internal implementation detail of a single class.
	* Each generated page is managed by a single class.
	* Client-server protocol provides more context
	* Simple access to log information using attribute maps.
	* Logs splitted by project/client/execution.
	* Logs organized in directories for faster access.
	* Cheap information have their own access point.
* Command line tool (testfarmserver) to setup and control a testfarm log
* Easy server deployment
	* WSGI method (recommended)
	* FastCGI method (for hostings with restrictions like DreamHost)
* Easy installation (pip install testfarm)
* History pages include a client status summary at the top
* Better plots. Removed the dependency on ploticus.
* Reporters:
	* Wrapper reporter for v1 clients attached to v2 loggers
	* Simplified and configurable IRC reporter
	* Configurable Mail reporter
* Tray icon applet (TestFarm Indicator) to monitor TestFarm status


