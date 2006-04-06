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

import unittest
from listeners import *
from testfarmclient import *

class Tests_TestFarmClient(unittest.TestCase):

	def test_constructor_with_one_task_repository(self):
		repository = Repository("repo name")
		repository.add_task( "taskname" , ["echo hello"] )
		dummylistener = DummyResultListener()
		client = TestFarmClient( 'a client', repository, testinglisteners = [ dummylistener ] )
		self.assertEquals("""\
BEGIN_REPOSITORY repo name
BEGIN_TASK taskname
('echo hello', 'ok', '', '', {})
END_TASK taskname
END_REPOSITORY repo name""", dummylistener.log() )


		


