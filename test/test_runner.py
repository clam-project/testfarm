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

from coloredtest import ColoredTestCase
from listeners import *
from runner import *

class Tests_Runner(ColoredTestCase):

	def test_constructor_with_one_task_repository(self):
		task = Task("project name", "client name", "task name")
		task.add_subtask( "subtaskname" , ["echo hello"] )
		dummylistener = DummyResultListener()
		runner = Runner( task, testinglisteners = [ dummylistener ] )
		self.assertEquals("""\
BEGIN_TASK task name
BEGIN_SUBTASK subtaskname
('echo hello', 'ok', '', '', {})
END_SUBTASK subtaskname
END_TASK task name""", dummylistener.log() )


		


