#
#  Copyright (c) 2006 Pau Arumi, Bram de Jong, Mohamed Sordo
#  and Universitat Pompeu Fabra
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#


from task import *
from serverlistener import ServerListener
from serverlistenerproxy import ServerListenerProxy

class Runner :
	"The interface to another modules. It runs a defined script and sends information to listeners."
	def __init__(self,
		task,
		continuous=False,
		first_run_always=True,
		local_base_dir = None,
		remote_server_url = None,
		verbose = False,
		testinglisteners = [],
		extra_listeners = [],
	) :
		"Runs a task defined in user's script"
		self.listeners = [ ConsoleResultListener() ]

		serverlistener = None # for keyboard interrupt purpose

		if remote_server_url:
			listenerproxy = ServerListenerProxy(
				client=task.client,
				service_url=remote_server_url,
				project=task.project
			)
			self.listeners.append( listenerproxy )
		if local_base_dir :
			serverlistener = ServerListener(
				client=task.client,
				logs_base_dir=local_base_dir + "/logs",
				project=task.project
			)
			self.listeners.append( serverlistener )

		server_to_push = None

		if testinglisteners:
			self.listeners = testinglisteners

		self.listeners += extra_listeners

		try :
			#do_subtasks at least one time
			new_commits_found = task.do_checking_for_new_commits( self.listeners, verbose=verbose ) #this creates a valid .idle file
			print "first_run_always ",first_run_always
			print "new commits_found ", new_commits_found
			if first_run_always or new_commits_found :
				task.do_subtasks( self.listeners, server_to_push = server_to_push, verbose=verbose )

			while continuous :
				new_commits_found = task.do_checking_for_new_commits( self.listeners, verbose=verbose )
				if new_commits_found:
					time.sleep(2) #avoid having executions with the same time
					task.do_subtasks( self.listeners, server_to_push = server_to_push, verbose=verbose )
				else:
					if server_to_push: #update idle time display
						server_to_push.update_static_html_files()
					time.sleep( task.seconds_idle )
		except KeyboardInterrupt :
			task.stop_execution_gently(self.listeners, server_to_push = server_to_push)

