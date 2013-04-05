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

		self.assertEqual(adaptee(1,2),
			(1,2))

	def test_expandfunction_voidExpanderKeepsSignature(self) :
		def expander(): return "booo"
		@expandfunction(expander)
		def adaptee(a, b): return a,b

		self.assertSignatureEqual(adaptee,
			"(a, b)")
		self.assertEqual(adaptee(1,2),
			(1,2))

	def _test_expandfunction_withExpanderArgs(self) :
		expanderReturns = []
		def expander(x): expanderReturns.append(x)
		@expandfunction(expander)
		def adaptee(a, b): return a,b

		self.assertSignatureEqual(adaptee,
			"(a, b)")
		self.assertEqual(adaptee(1,2),
			(1,2))
		self.assertEqual(expanderReturns, [3])




if __name__=="__main__" :
	unittest.main()


