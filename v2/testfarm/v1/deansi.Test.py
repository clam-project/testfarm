#!/usr/bin/python
"""
Copyright 2012 David Garcia Garzon

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

from deansi import *

html_template = """\
<style>
.ansi_terminal { background-color: #222; color: #cfc; }
%s
</style>
<div class='ansi_terminal'>%s</div>
"""
import unittest

class DeansiTest(unittest.TestCase) :
	def assertDeansiEquals(self, expected, inputText) :
		return self.assertEquals(expected, deansi(inputText))

	def test_html(self) :
		self.assertDeansiEquals(
			'weee&lt;&gt;&amp;',
			'weee<>&',
		)

	def test_ansiAttributes_withSingleAttribute(self) :
		self.assertEquals(
			([45],'text'),
			ansiAttributes("[45mtext")
		)

	def test_ansiAttributes_withManyAttributes(self) :
		self.assertEquals(
			([45,54,2],'text'),
			ansiAttributes("[45;54;2mtext")
		)

	def test_ansiAttributes_withNoAttributes(self) :
		self.assertEquals(
			([], 'text'),
			ansiAttributes("text")
		)

	def test_ansiAttributes_withNoNumbers(self) :
		self.assertEquals(
			([], '[a;bmtext'),
			ansiAttributes("[a;bmtext")
		)

	def test_ansiAttributes_emptyReturnsZero(self) :
		self.assertEquals(
			([0], 'text'),
			ansiAttributes("[mtext")
		)

	def test_ansiState_bright(self) :
		self.assertEquals(
			(set(['bright']), None, None),
			ansiState(1, set(), None, None),
		)

	def test_ansiState_faint(self) :
		self.assertEquals(
			(set(['faint']), None, None),
			ansiState(2, set(), None, None),
		)

	def test_ansiState_italic(self) :
		self.assertEquals(
			(set(['italic']), None, None),
			ansiState(3, set(), None, None),
		)

	def test_ansiState_underscore(self) :
		self.assertEquals(
			(set(['underscore']), None, None),
			ansiState(4, set(), None, None),
		)

	def test_ansiState_blink(self) :
		self.assertEquals(
			(set(['blink']), None, None),
			ansiState(5, set(), None, None),
		)

	def test_ansiState_reverse(self) :
		self.assertEquals(
			(set(['reverse']), None, None),
			ansiState(7, set(), None, None),
		)

	def test_ansiState_hide(self) :
		self.assertEquals(
			(set(['hide']), None, None),
			ansiState(8, set(), None, None),
		)

	def test_ansiState_addTwoAttributes(self) :
		self.assertEquals(
			(set(['bright', 'blink']), None, None),
			ansiState(1, set(['blink']), None, None),
		)

	def test_ansiState_clear_clearsBits(self) :
		self.assertEquals(
			(set(), None, None),
			ansiState(0, set(['blink', 'whatever']), None, None),
		)

	def test_ansiState_setForeground(self) :
		self.assertEquals(
			(set(), 'green', None),
			ansiState(32, set(), 'green', None),
		)

	def test_ansiState_setForegroundTwice(self) :
		self.assertEquals(
			(set(), 'red', None),
			ansiState(31, set(), 'green', None),
		)

	def test_ansiState_setBackground(self) :
		self.assertEquals(
			(set(), None, 'yellow'),
			ansiState(43, set(), None, None),
		)

	def test_ansiState_clearClearsFore(self) :
		self.assertEquals(
			(set(), None, None),
			ansiState(0, set(), 'green', None),
		)

	def test_ansiState_clearClearsBack(self) :
		self.assertEquals(
			(set(), None, None),
			ansiState(0, set(), None, 'green'),
		)

	def test_ansiState_noForeground(self) :
		self.assertEquals(
			(set(['blink','inverse']), None, 'red'),
			ansiState(39, set(['blink','inverse']), 'green', 'red')
			)

	def test_ansiState_noBackground(self) :
		self.assertEquals(
			(set(['blink','inverse']), 'green', None),
			ansiState(49, set(['blink','inverse']), 'green', 'red')
			)

	def test_ansiState_resetAttribute(self) :
		self.assertEquals(
			(set(['inverse']), 'green', 'red'),
			ansiState(25, set(['blink','inverse']), 'green', 'red')
			)

	def test_ansiState_resetAttributeNotInThere(self) :
		self.assertEquals(
			(set(['inverse']), 'green', 'red'),
			ansiState(25, set(['inverse']), 'green', 'red')
			)

	def test_stateToClasses_withAttribs(self) :
		self.assertEquals(
			"ansi_blink ansi_bright",
			stateToClasses(set(['bright','blink']), None, None)
			)

	def test_stateToClasses_withFore(self) :
		self.assertEquals(
			"ansi_red",
			stateToClasses(set(), 'red', None)
			)

	def test_stateToClasses_withBack(self) :
		self.assertEquals(
			"ansi_bgred",
			stateToClasses(set(), None, 'red')
			)

	def test_stateToClasses_withAll(self) :
		self.assertEquals(
			"ansi_blink ansi_inverse ansi_green ansi_bgred",
			stateToClasses(set(['blink','inverse']), 'green', 'red')
			)

	def test_deansi_withCodes(self) :
		self.assertEquals(
			'this should be <span class=\'ansi_red\'>red</span> and this not',
			deansi('this should be \033[31mred\033[0m and this not'),
		)

	def test_deansi_emptyAttributeClears(self) :
		self.assertEquals(
			'this should be <span class=\'ansi_red\'>red</span> and this not',
			deansi('this should be \033[31mred\033[m and this not'),
		)

	def test_deansi_withComplexCodes(self) :
		self.assertEquals(
			'this should be <span class=\'ansi_red\'>red</span>'
			'<span class=\'ansi_bright ansi_red ansi_bggreen\'> and green background</span> and this not',
			deansi('this should be \033[31mred\033[42;1m and green background\033[0m and this not'),
		)

	def test_deansi_takesMultiline(self) :
		self.assertEquals(
			'this should be <span class=\'ansi_red\'>\nred</span>'
			'<span class=\'ansi_bright ansi_red ansi_bggreen\'> and green \nbackground\n</span> and this not',
			deansi('this should be \033[31m\nred\033[42;1m and green \nbackground\n\033[0m and this not'),
		)

	def test_backToBack(self) :
		terminalInput = """\
Normal colors:
	\033[30mblack\033[0m\
	\033[31mred\033[0m\
	\033[32mgreen\033[0m\
	\033[33myellow\033[0m\
	\033[34mblue\033[0m\
	\033[35mmagenta\033[0m\
	\033[36mcyan\033[0m\
	\033[37mwhite\033[0m\
	\033[39mdefault\033[0m
Bright colors:
	\033[1;30mblack\033[0m\
	\033[1;31mred\033[0m\
	\033[1;32mgreen\033[0m\
	\033[1;33myellow\033[0m\
	\033[1;34mblue\033[0m\
	\033[1;35mmagenta\033[0m\
	\033[1;36mcyan\033[0m\
	\033[1;37mwhite\033[0m\
	\033[1;39mdefault\033[0m
Background colors:
	\033[40mblack\033[0m\
	\033[41mred\033[0m\
	\033[42mgreen\033[0m\
	\033[43myellow\033[0m\
	\033[44mblue\033[0m\
	\033[45mmagenta\033[0m\
	\033[46mcyan\033[0m\
	\033[47mwhite\033[0m\
	\033[49mdefault\033[0m
Attributes:
	\033[1mbright\033[0m
	\033[2mfaint\033[0m
	\033[3mitalic\033[0m
	\033[4munderscore\033[0m
	\033[5mblink\033[0m
	\033[6mdouble blink\033[0m <- not implemented
	\033[7mreverse\033[0m <- TODO: Find a better way to implement it
	\033[8mhide\033[0m <- It's hidden, you can still select and copy it
	\033[9mstrike\033[0m

Activating \033[31mred and then \033[43mdark yellow
background and then activating \033[32mgreen foreground
now changing attribute to \033[1mbright and then
\033[21mreseting it without changing colors.
\033[44mblue background and \033[5mblink attribute,
\033[49mdefault background, unsetting \033[25mblink,
unsetting \033[39m foreground and \033[0mall attribs.
"""
		print terminalInput
		expected = file("deansi-b2b.html").read()
		result = html_template % (styleSheet(), deansi(terminalInput))

		if (result!=expected) :
			file("deansi-failed.html","w").write(result)
		self.assertEquals(expected, result)

if __name__ == "__main__" :
	unittest.main()


