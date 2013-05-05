#!/usr/bin/python

from SvnSandbox import SvnSandbox
import testfarm.utils as utils
import os
import unittest

class SvnSandboxTest(unittest.TestCase) :
	def x(self, command) :
		return utils.run(command%self.defs)
	def inSandbox(self, file) :
		return os.path.join(self.defs['sandbox'],file)
	def addFile(self, file, commit=True) :
		self.x('touch %%(sandbox)s/%s'%file)
		self.x('svn add %%(sandbox)s/%s'%file)
		if commit :
			self.commitFile(file, "added %s" % file)
	def removeFile(self, file, commit=True) :
		self.x('svn rm %%(sandbox)s/%s'%file)
		if commit :
			self.commitFile(file, "removed %s" % file)
	def addRevisions(self, file, n, commit=True) :
		for i in xrange(n) :
			self.x('echo Change %s >> %%(sandbox)s/%s'%(i,file))
			if commit :
				self.commitFile(file, "change %i of %s"%(i,file))
	def pushRevision(self) :
		self.revisions.append(str(len(self.revisions)))
		print "REVISIONS", self.revisions
	def commitFile(self, file, message) :
		self.x('svn commit %%(sandbox)s/%s -m"%s"'%(file,message))
		self.x('svn up %(sandbox)s')
		self.pushRevision()
	def commitAll(self, message) :
		self.x('svn commit %%(sandbox)s/ -m"%s"'%(message))
		self.x('svn up %(sandbox)s')
		self.pushRevision()
	def rewind(self, revisions=1) :
		target = int(self.current())-revisions
		self.x('svn up -r%s %%(sandbox)s'%(target))
	def current(self) :
		output = utils.output('svn info -r BASE %(sandbox)s | grep ^Revision: '%self.defs)
		print "CURRENT",output.split()
		return output.split()[-1]

	def setUp(self) :
		self.defs = dict(
			username = "myuser",
			testdir = os.path.join(os.getcwd(),'testdir'),
			repo    = os.path.join(os.getcwd(),'testdir/repo'),
			sandbox = os.path.join(os.getcwd(),'testdir/sandbox1'),
			)
		self.x('rm -rf %(testdir)s')
		self.x('mkdir -p %(testdir)s')
		self.revisions = ['0']
		self.x('svnadmin create %(repo)s')
		self.x('svn co --username %(username)s file://%(repo)s %(sandbox)s')

	def tearDown(self) :
		""" """
#		self.x('svn log %(sandbox)s')
		self.x('rm -rf %(testdir)s')

	def test_state(self) :
		self.addFile('file')
		self.addRevisions('file',3)
		s = SvnSandbox(self.defs['sandbox'])
		self.assertEquals(self.revisions[4], s.state())
		self.rewind(3)
		self.assertEquals(self.revisions[1], s.state())

	def test_remoteState(self) :
		self.addFile('file')
		self.addRevisions('file',3)
		s = SvnSandbox(self.defs['sandbox'])
		self.assertEquals(self.revisions[4], s.remoteState())
		self.rewind(3)
		self.assertEquals(self.revisions[4], s.remoteState())

	def test_update(self) :
		self.addFile('file')
		self.addRevisions('file',3)
		s = SvnSandbox(self.defs['sandbox'])
		self.rewind(3)
		s.update()
		self.assertEquals(self.revisions[4], s.state())

	def test_update_withConflictPostpones(self) :
		self.addFile('file')
		self.addRevisions('file',3)
		s = SvnSandbox(self.defs['sandbox'])
		self.rewind(2)
		self.addRevisions('file',1, False) # local conflicting change
		s.update()
		self.assertEquals(self.revisions[4], s.state())
		# TODO: Check that file is left in conflict

	def test_pendingCommits(self) :
		self.addFile('file')
		self.addRevisions('file',3)
		self.rewind(3)
		s = SvnSandbox(self.defs['sandbox'])
		self.assertEquals(
			self.revisions[-3:], s.pendingUpdates())

	def test_guilty(self) :
		self.addFile('file')
		self.addRevisions('file',3)
		self.rewind(3)
		s = SvnSandbox(self.defs['sandbox'])
		self.assertEquals(
			[
				(rev, self.defs['username'], "change %i of file"%i)
				for i, rev in enumerate(self.revisions[-3:])
			], s.guilty())

	def test_pendingChanges(self) :
		self.addFile('remoteChange', False)
		self.addFile('remoteRemove', False)
		self.addFile('localRemove', False)
		self.addFile('localChange', False)
		self.addFile('nonsvnRemove', False)
		self.commitAll("State were we want to go back")

		self.addRevisions('remoteChange',1, False)
		self.addFile('remoteAdd', False)
		self.removeFile('remoteRemove', False)
		self.commitAll("State we want to update to")
		self.rewind(1)

		# local modifications
		self.addRevisions('localChange', 1, False)
		self.removeFile('localRemove', False)
		self.addFile('localAdd', False)
		self.x('echo nonsvnAdd > %(sandbox)s/nonsvnAdd')
		self.x('rm %(sandbox)s/nonsvnRemove')

		s = SvnSandbox(self.defs['sandbox'])
		self.maxDiff = None
		self.assertEquals(
			[
				(self.defs['sandbox'],           ('normal', 'none', 'modified', 'none')),
				(self.inSandbox('localAdd'),     ('added', 'none', 'none', 'none')),
				(self.inSandbox('localChange'),  ('modified', 'none', 'none', 'none')),
				(self.inSandbox('localRemove'),  ('deleted', 'none', 'none', 'none')),
				(self.inSandbox('nonsvnAdd'),    ('unversioned', 'none', 'none', 'none')),
				(self.inSandbox('nonsvnRemove'), ('missing', 'none', 'none', 'none')),
				(self.inSandbox('remoteAdd'),    ('none', 'none', 'added', 'none')),
				(self.inSandbox('remoteChange'), ('normal', 'none', 'modified', 'none')),
				(self.inSandbox('remoteRemove'), ('normal', 'none', 'deleted', 'none')),

			], sorted(s._pendingChanges()))

	def test_hasPendingChanges_whenNoPendingChanges(self) :
		self.addFile('remoteChange', False)
		self.addFile('remoteRemove', False)
		self.addFile('localRemove', False)
		self.addFile('localChange', False)
		self.addFile('nonsvnRemove', False)
		self.commitAll("State were we want to go back")

		s = SvnSandbox(self.defs['sandbox'])
		self.assertFalse(s.hasPendingChanges())

	def test_hasPendingChanges_whenMissingFile(self) :
		self.addFile('nonsvnRemove')
		self.x('rm %(sandbox)s/nonsvnRemove')

		s = SvnSandbox(self.defs['sandbox'])
		self.assertTrue(s.hasPendingChanges())

	def test_hasPendingChanges_whenPendingModification(self) :
		self.addFile('remoteChange')
		self.addRevisions('remoteChange',1)
		self.rewind(1)

		s = SvnSandbox(self.defs['sandbox'])
		self.assertTrue(s.hasPendingChanges())

	def test_hasPendingChanges_whenPendingRemove(self) :
		self.addFile('remoteRemove')
		self.removeFile('remoteRemove')
		self.rewind(1)

		s = SvnSandbox(self.defs['sandbox'])
		self.assertTrue(s.hasPendingChanges())

	def test_hasPendingChanges_whenPendingAdd(self) :
		self.addFile('remoteAdd')
		self.rewind(1)

		s = SvnSandbox(self.defs['sandbox'])
		self.assertTrue(s.hasPendingChanges())

	def test_hasPendingChanges_whenLocalChanges(self) :
		self.addFile('localRemove', False)
		self.addFile('localChange', False)
		self.commitAll("State were we want to go back")

		# any local modifications (but non-svn deletion)
		self.addRevisions('localChange', 1, False)
		self.removeFile('localRemove', False)
		self.addFile('localAdd', False)
		self.x('echo nonsvnAdd > %(sandbox)s/nonsvnAdd')

		s = SvnSandbox(self.defs['sandbox'])
		self.maxDiff = None
		self.assertFalse(s.hasPendingChanges())


if __name__ == '__main__' :
	unittest.main()


