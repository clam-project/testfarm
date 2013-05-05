#!/usr/bin/python

import xml.etree.cElementTree as ET
#import xml.etree.ElementTree as ET # Python 2.5
import testfarm.utils as utils


class SvnSandbox(object) :
	def __init__(self, sandbox, verbose=False ) :
		self.sandbox = sandbox
		self._verbose = verbose
		self.conflictResolution = 'postpone'
	def _run(self, command) :
		utils.run(
			command%self.__dict__,
			message = None if self._verbose else "",
			log = utils.null(),
			)

	def _output(self, command) :
		return utils.output(
			command%self.__dict__,
			message = None if self._verbose else "",
			)

	# TODO: Not unit tested
	def location(self) :
		return self.sandbox

	def state(self) :
		xml = self._output("svn --xml info %(sandbox)s")
		info = ET.fromstring(xml)
		return info.find("entry").get('revision')
		# text based implementation (needs LANG and risky)
		return self._output("LANG=C svn info %(sandbox)s | grep ^Revision: ").split()[-1]

	def remoteState(self) :
		xml = self._output("svn --xml info -rHEAD %(sandbox)s")
		info = ET.fromstring(xml)
		return info.find("entry").get('revision')
		# text based implementation (needs LANG and risky)
		return self._output("LANG=C svn info %(sandbox)s | grep ^Revision: ").split()[-1]

	def update(self, revision=None) :
		self._run("svn up --accept %(conflictResolution)s %(sandbox)s")

	def pendingUpdates(self) :
		xml = self._output("svn --xml log %(sandbox)s -rBASE:HEAD")
		log = ET.fromstring(xml)
		return [logentry.get('revision') for logentry in log.findall("logentry") ][1:]

	def guilty(self) :
		xml = self._output("svn --xml log %(sandbox)s -rBASE:HEAD")
		log = ET.fromstring(xml)
		return [(
			logentry.get('revision'),
			logentry.find('author').text,
			logentry.find('msg').text,
			) for logentry in log.findall("logentry") ][1:]

	def _pendingChanges(self) :
		xml = self._output("svn status --xml -u %(sandbox)s ")
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


