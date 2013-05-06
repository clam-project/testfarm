TestFarm
========

What is it?
-----------

TestFarm is a continuous integration platform.
Several distributed TestFarm clients are monitoring periodically
at the version control system for updates.
When an update is detected, an execution on the client is started
and results are reported to a centralized server
which collects them in a web site.

Unlike other continuous integration tools,
the server is not explicitly starting the executions.
The server is the only machine that requires a public IP.
Each client may choose the check pace, not running for a while,
or even explicitly run one without any pending update.
This is better suited for projects of volunteer developers,
with no cash for a dedicated clients running 7/24.
This way, volunteers can run the client to their convenience.

Features
--------

* Python based: A client is defined with a Python script,
  a dynamic language with gives you a lot of flexibility.
* Static generated pages: The generated website
  is not relying on php, python or anything.
  They are pure html + css + javascript pages.
  You can copy as is to any webserver.
* Collects stats such as SLOC, number of tests... and
  present them in a time graph.


This documentation is WIP.

More info at [this blog][here].

[here]: http://canvoki.net/coder/blog/2013-03-21-refactoring-the-testfarm-server.html




