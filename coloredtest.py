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

class ColoredTestCase(unittest.TestCase):
	def assertEquals(self, expected, result):
		if expected == result :
			return
		expectedstr = str(expected)
		resultstr = str(result)
		red = "\x1b[31;01m"
		green ="\x1b[32;01m"
		yellow = "\x1b[33;01m" # unreadable on white backgrounds
		cyan = "\x1b[36;01m"
		normal = "\x1b[0m"

		index_diff = 0
		for i in range(len(resultstr)):
			if expectedstr[i]!=resultstr[i]:
				index_diff = i
				break
		
		msg = "\n<expected>\n%s%s%s%s%s\n</expected>\n" % (cyan, expectedstr[:index_diff], green, expectedstr[index_diff:], normal)
		msg += "\n<but was>\n%s%s%s%s%s\n</but was>" % (cyan, resultstr[:index_diff], red, resultstr[index_diff:], normal)
	
		self.fail(msg)
		
