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

from reporter import *
import os
import unittest

class MockUp :
	def singleArg(self, minutes) : pass
	def optional(self, param1=3) : pass
	def optionalKwds(self, param1=3, **kwds) : pass

class ClassLoggerTest(unittest.TestCase) :
	def test_calls_noCall(self) :
		r = LogWrapper(MockUp())
		self.assertEqual(r.calls(), [
			])

	def test_calls_singleCall(self) :
		r = LogWrapper(MockUp())
		r.singleArg(23)
		self.assertEqual(r.calls(), [
			("singleArg", dict(minutes=23)),
			])

	def test_calls_keywordCall(self) :
		r = LogWrapper(MockUp())
		r.singleArg(minutes=23)
		self.assertEqual(r.calls(), [
			("singleArg", dict(minutes=23)),
			])

	def test_calls_keywordSpecifiedTwice(self) :
		r = LogWrapper(MockUp())
		try :
			r.singleArg(40, minutes=23)
			self.fail("Exception expected")
		except TypeError as e :
			self.assertMultiLineEqual(e.message,
				"singleArg() got multiple values "
					"for keyword argument 'minutes'"
			)

	def test_calls_optional(self) :
		r = LogWrapper(MockUp())
		r.optional()
		self.assertEqual(r.calls(), [
			("optional", dict(param1=3)),
			])

	def test_calls_optionalKwds(self) :
		r = LogWrapper(MockUp())
		r.optionalKwds(nonspecified=5)
		self.assertEqual(r.calls(), [
			("optionalKwds", dict(param1=3, nonspecified=5)),
			])

	def test_calls_tooManyArgs(self) :
		r = LogWrapper(MockUp())
		try :
			r.singleArg(1, 2)
			self.fail("Exception expected")
		except TypeError as e :
			self.assertMultiLineEqual(e.message,
				"singleArg expected at most 2 arguments, got 3"
			)


class MultiReporterTest(unittest.TestCase) :
	def test_add_one(self) :
		r = LogWrapper(MockUp())
		m = MultiReporter()
		m.add(r)

		m.singleArg(minutes=40)
		self.assertEqual(r.calls(), [
			("singleArg", dict(minutes=40)),
			])

	def test_add_many(self) :
		r1 = LogWrapper(MockUp())
		r2 = LogWrapper(MockUp())
		m = MultiReporter()
		m.add(r1)
		m.add(r2)

		m.singleArg(minutes=40)
		self.assertEqual(r1.calls(), [
			("singleArg", dict(minutes=40)),
			])
		self.assertEqual(r2.calls(), [
			("singleArg", dict(minutes=40)),
			])


if __name__ == "__main__" :
	unittest.main()


