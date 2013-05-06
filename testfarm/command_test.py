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

from command import *
import os
import unittest

class CommandTest(unittest.TestCase) :
	def test_run_whenOk(self) :
		c = Command("true")
		self.assertEqual(c.run(), (
			"",
			True, None, {}))

	def test_run_whenKo(self) :
		c = Command("false")
		self.assertEqual(c.run(), (
			"",
			False, None, {}))

	def test_run_stdout(self) :
		c = Command("echo output")
		self.assertEqual(c.run(), (
			"output\n",
			True, None, {}))

	def test_run_stderr(self) :
		c = Command("echo error >&2")
		self.assertEqual(c.run(), (
			"\033[31merror\n\033[0m",
			True, None,  {}))

	def test_run_substitutions(self) :
		c = Command("echo {whatyousay}")
		self.assertEqual(
			c.run(subst=dict(whatyousay="go up")
			), (
			"go up\n",
			True, None,  {}))

	def test_run_info(self) :
		def info(output) :
			return "Bo\n"+output+"Ba\n"
		c = Command("echo inner", info=info)
		self.assertEqual(
			c.run(), (
			"inner\n",
			True, "Bo\ninner\nBa\n", {}))

	def test_run_info(self) :
		def info(output) :
			return "Bo\n"+output+"Ba\n"
		c = Command("echo inner", info=info)
		self.assertEqual(
			c.run(), (
			"inner\n",
			True, "Bo\ninner\nBa\n", {}))

	def test_run_okFunction(self) :
		def invertStatus(output, ok) :
			return not ok
		c = Command("true", ok=invertStatus)
		self.assertEqual(
			c.run(), (
			"",
			False, None, {}))

	def test_run_okFunction_whenFalse(self) :
		def invertStatus(output, ok) :
			return not ok
		c = Command("false", ok=invertStatus)
		self.assertEqual(
			c.run(), (
			"",
			True, None, {}))

	def test_run_stat_withAFunction(self) :
		c = Command("echo 14", value=int)
		self.assertEqual(
			c.run(), (
			"14\n",
			True, None, dict(value=14)))

	def test_run_stat_withExplicitValue(self) :
		c = Command("echo 14", value=43)
		self.assertEqual(
			c.run(), (
			"14\n",
			True, None, dict(value=43)))

	def test_run_cwd(self) :
		cwd = os.getcwd()
		newdir = os.path.abspath(os.path.join(cwd,".."))
		c = Command("pwd")
		self.assertEqual(
			c.run(cwd=newdir), (
			newdir+"\n",
			True, None, {}))
		self.assertEqual(cwd, os.getcwd())



if __name__ == "__main__" :
	unittest.main()


