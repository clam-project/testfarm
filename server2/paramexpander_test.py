#!/usr/bin/python

from paramexpander import expandfunction
import unittest

class ParamExpanderTest(unittest.TestCase) :

	def setUp(self) :
		pass

	def tearDown(self) :
		pass

	def assertSignatureEqual(self, f1, signature) :
		from inspect import getargspec, formatargspec
		self.assertEqual( formatargspec(*getargspec(f1)), signature)


	def test_assertSignatureEqual_whenEmpty(self) :
		def adaptee(): pass
		self.assertSignatureEqual(adaptee,
			"()")

	def test_assertSignatureEqual_positionalParams(self) :
		def adaptee(a, b): pass
		self.assertSignatureEqual(adaptee,
			"(a, b)")

	def test_assertSignatureEqual_optionalParams(self) :
		def adaptee(a, b=3): pass
		self.assertSignatureEqual(adaptee,
			"(a, b=3)")

	def test_assertSignatureEqual_args(self) :
		def adaptee(a, *b): pass
		self.assertSignatureEqual(adaptee,
			"(a, *b)")

	def test_assertSignatureEqual_keybd(self) :
		def adaptee(a, **b): pass
		self.assertSignatureEqual(adaptee,
			"(a, **b)")

	def test_expandfunction_keepsName(self) :
		expanderReturns = []
		def expander(): pass
		@expandfunction(expander)
		def adaptee(): return None

		self.assertEqual(adaptee.__name__, "adaptee")

	def test_expandfunction_keepsDocs(self) :
		expanderReturns = []
		def expander(): pass
		@expandfunction(expander)
		def adaptee(): "documentation"

		self.assertEqual(adaptee.__doc__, "documentation")

	def test_expandfunction_expanderIsCalled(self) :
		expanderCalled = []
		def expander(): expanderCalled.append("yes")
		@expandfunction(expander)
		def adaptee(a, b): return a,b

		self.assertFalse(expanderCalled)
		adaptee(1,2)
		self.assertTrue(expanderCalled)

	def test_expandfunction_returnsAdapteeResult(self) :
		def expander(): return "booo"
		@expandfunction(expander)
		def adaptee(a, b): return a,b

		self.assertEqual(adaptee(1,2), (1,2))

	def test_expandfunction_voidExpanderKeepsSignature(self) :
		def expander(): return "booo"
		@expandfunction(expander)
		def adaptee(a, b): return a,b

		self.assertSignatureEqual(adaptee, "(a, b)")
		self.assertEqual(adaptee(1,2), (1,2))

	def test_expandfunction_withExpanderArgs(self) :
		expanderReturns = []
		def expander(x): expanderReturns.append(x)
		@expandfunction(expander)
		def adaptee(a, b): return a,b

		self.assertSignatureEqual(adaptee, "(a, b, x)")
		self.assertEqual(adaptee(1,2,3), (1,2))
		self.assertEqual(expanderReturns, [3])

	def test_expandfunction_withCommonArgs(self) :
		expanderReturns = []
		def expander(b): expanderReturns.append(b)
		@expandfunction(expander)
		def adaptee(a, b): return a,b

		self.assertSignatureEqual(adaptee, "(a, b)")
		self.assertEqual(adaptee(1,2), (1,2))
		self.assertEqual(expanderReturns, [2])

	def test_expandfunction_optionalArgsInExpander(self) :
		expanderReturns = []
		def expander(x,y=66): expanderReturns.append((x,y))
		@expandfunction(expander)
		def adaptee(a, b): return a,b

		self.assertSignatureEqual(adaptee, "(a, b, x, y=66)")
		self.assertEqual(adaptee(1,2,3), (1,2))
		self.assertEqual(expanderReturns, [(3,66)])

	def test_expandfunction_optionalArgsInAdaptee(self) :
		expanderReturns = []
		def expander(x): expanderReturns.append(x)
		@expandfunction(expander)
		def adaptee(a, b=66): return a,b

		self.assertSignatureEqual(adaptee, "(a, x, b=66)")
		self.assertEqual(adaptee(1,2,3), (1,3))
		self.assertEqual(expanderReturns, [2])

	def test_expandfunction_optionalArgsInBoth(self) :
		expanderReturns = []
		def expander(x, y=99): expanderReturns.append((x,y))
		@expandfunction(expander)
		def adaptee(a, b=66): return a,b

		self.assertSignatureEqual(adaptee, "(a, x, b=66, y=99)")
		self.assertEqual(adaptee(1,2,3,4), (1,3))
		self.assertEqual(expanderReturns, [(2,4)])






"""
TODO:
+ adaptee name remains
+ adaptee doc remains
+ optionals in expander
- optionals in adaptee
- optionals in both sorted adaptee, then expander
- optional in expander remains optional
- optional in adaptee remains optional
- optional in both, takes adaptee value (yes?)
- keyword call allows disordering
- varargs, what to do with them?
- keywordargs, what to do with them?
"""



if __name__=="__main__" :
	unittest.main()


