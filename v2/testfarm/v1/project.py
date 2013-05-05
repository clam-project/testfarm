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

class Project :
	"Defines a project, with its name and descriptions. It also supports new added attributes."
	def __init__(self, project_name, brief_description = None, long_description= None) :
		assert project_name, "Error, project name was expected"
		self.name = project_name
		self.brief_description = brief_description
		self.long_description = long_description
		self.attributes = {}


	def set_attribute(self, attribute_name, attribute_value):
		"Adds an attribute defined by user"
		self.attributes[attribute_name] = attribute_value

