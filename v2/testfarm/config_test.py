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

from config import *
import unittest
from reporter import MockUpReporter
import os

class ConfigTest(unittest.TestCase) :

	def setUp(self) :
		self._toDelete = []

	def tearDown(self) :
		for f in self._toDelete :
			os.unlink(f)

	def writeFile(self, name, content) :
		self._toDelete.append(name)
		with open(name,'w') as f:
			f.write(content)


	def test_attribute(self) :
		c = Config(
				var = 'value',
			)
		self.assertEqual(c.var, "value")

	def test_attribute_notPresent(self) :
		c = Config(
			var = 'value',
			)
		try :
			c.badValue
			self.fail("Exception expected")
		except AttributeError as e:
			self.assertEqual(e.message,
				"'Config' object has no attribute 'badValue'")

	def test_setAttribute(self) :
		c = Config(
			var = 'value',
			)
		self.assertEqual("newVar" in c, False)
		c.newVar = 3
		self.assertEqual(c.newVar, 3)
		self.assertEqual("newVar" in c, True)

	# TODO: Protect that
	def _test_setAttribute_reserved(self) :
		c = Config(
			var = 'value',
			)
		try :
			c.subst = 3
			self.fail("Exception expected")
		except KeyError as e :
			self.assertEqual(e.message,
				"'subst' is a reserved key")

	def test_subst_withNoFormatting(self) :
		c = Config(
			var='value',
			)
		self.assertEqual(c.subst("text"), "text")

	def test_subst_withFormatting(self) :
		c = Config(
			var='value',
			)
		self.assertEqual(c.subst("{var}"), "value")

	def test_subst_withWrongKey(self) :
		c = Config(
			var='value',
			)
		try :
			c.subst("{wrong}")
			self.fail("Exception expected")
		except KeyError as e :
			self.assertEqual(e.message, "wrong")

	def test_load(self) :
		self.writeFile("fixtureconfig",
			"var = 2"
			)
		c = Config()
		c.load("fixtureconfig")
		self.assertEqual(c.var, 2)

	def test_load_overrides(self) :
		self.writeFile("fixtureconfig",
			"var1 = 2"
			)
		c = Config(var1 = 3, var2=4)
		c.load("fixtureconfig")
		self.assertEqual(c.var1, 2)
		self.assertEqual(c.var2, 4)

	def test_load_subConfig(self) :
		self.writeFile("fixtureconfig",
			"var1 = 2\n"
			"class subvar :\n"
			"	var1 = 'value'\n"
			)
		c = Config(var1 = 3, var2=4)
		c.subvar = Config()
		c.load("fixtureconfig")
		self.assertEqual(c.var1, 2)
		self.assertEqual(c.subvar.var1, 'value')





if __name__ == "__main__" :
	unittest.main()


