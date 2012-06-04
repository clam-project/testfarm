#!/usr/bin/python

import xml.etree.cElementTree as ET
#import xml.etree.ElementTree as ET # Python 2.5
import utils


class SvnSandbox(object) :
	def __init__(self, sandbox ) :
		self.sandbox = sandbox
		self.conflictResolution = 'postpone'

	# TODO: Not unit tested
	def location(self) :
		return self.sandbox

	def state(self) :
		xml = utils.output("svn --xml info %(sandbox)s"%self.__dict__)
		info = ET.fromstring(xml)
		return info.find("entry").get('revision')
		# text based implementation (needs LANG and risky)
		return utils.output("LANG=C svn info %(sandbox)s | grep ^Revision: "%self.__dict__).split()[-1]

	def remoteState(self) :
		xml = utils.output("svn --xml info -rHEAD %(sandbox)s"%self.__dict__)
		info = ET.fromstring(xml)
		return info.find("entry").get('revision')
		# text based implementation (needs LANG and risky)
		return utils.output("LANG=C svn info %(sandbox)s | grep ^Revision: "%self.__dict__).split()[-1]

	def update(self, revision=None) :
		utils.run("svn up --accept %(conflictResolution)s %(sandbox)s"%self.__dict__)

	def pendingUpdates(self) :
		xml = utils.output("svn --xml log %(sandbox)s -rBASE:HEAD"%self.__dict__)
		log = ET.fromstring(xml)
		return [logentry.get('revision') for logentry in log.findall("logentry") ][1:]

	def guilty(self) :
		xml = utils.output("svn --xml log %(sandbox)s -rBASE:HEAD"%self.__dict__)
		log = ET.fromstring(xml)
		return [(
			logentry.get('revision'),
			logentry.find('author').text,
			logentry.find('msg').text,
			) for logentry in log.findall("logentry") ][1:]

	def _pendingChanges(self) :
		xml = utils.output("svn status --xml -u %(sandbox)s "%self.__dict__)
		log = ET.fromstring(xml)
		result = []
		def get(elementOrNot, xmlProperty) :
			return 'none' if elementOrNot is None else elementOrNot.get(xmlProperty, 'none')
		for entry in log.getiterator("entry") :
			lstatus = entry.find("wc-status")
			rstatus = entry.find("repos-status")
			litem = get(lstatus,'item')
			lprop = get(lstatus,'prop')
			ritem = get(rstatus,'item')
			rprop = get(rstatus,'prop')
			result.append( ( entry.get('path'), ( litem, lprop, ritem, rprop)))
		return result

	def hasPendingChanges(self) :
		for path, (litem, lprop, ritem, rprop) in self._pendingChanges() :
			if litem == 'missing' : return True
			if ritem != 'none' : return True
			if rprop != 'none' : return True
		return False


