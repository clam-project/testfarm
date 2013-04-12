#!/usr/bin/python
"""
Copyright 2013 David Garcia Garzon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from client import *
import unittest
from reporter import MockUpReporter

class ClientTest(unittest.TestCase) :

	def setupClient(self, **kwds) :
		return Client(**kwds)

	def test_now_whenNotFixed(self) :
		c = self.setupClient()
		before = datetime.datetime.now()
		now = c.now
		after = datetime.datetime.now()
		self.assertTrue(before < now)
		self.assertTrue(now < after)
		
	def test_now_whenFixed(self) :
		c = self.setupClient()
		c.now = datetime.datetime(2000,01,02,03,04,05)
		self.assertEqual(c.now, datetime.datetime(2000,01,02,03,04,05))
		
	def test_now_whenReset(self) :
		c = self.setupClient()
		c.now = datetime.datetime(2000,01,02,03,04,05)
		c.now = None
		before = datetime.datetime.now()
		now = c.now
		after = datetime.datetime.now()
		self.assertTrue(before < now)
		self.assertTrue(now < after)

	def test_subst_withNoFormatting(self) :
		c = self.setupClient(
			var='value',
			)
		self.assertEqual(c.subst("text"), "text")

	def test_subst_withFormatting(self) :
		c = self.setupClient(
			var='value',
			)
		self.assertEqual(c.subst("{var}"), "value")

	def test_subst_withWrongKey(self) :
		c = self.setupClient(
			var='value',
			)
		try :
			c.subst("{wrong}")
			self.fail("Exception expected")
		except KeyError as e :
			self.assertEqual(e.message, "wrong")


	def _test_addReporter(self) :
		c = self.setupClient()
		r = MockUpReporter()
		c.addReporter(r)
		c.run()
		self.assertEqual(r.calls(), [
		])






if __name__ == "__main__" :
	unittest.main()


