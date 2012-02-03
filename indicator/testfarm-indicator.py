#!/usr/bin/python

"""
What i want to know:
- Given a failed run:
	- change set (authors, dates, descriptions, files) since the last green run
	- the last green run should be stored as well as the revision set
	- which is the failing task, subtask and command
	- which is the output of the failing command
"""


from PyQt4 import QtCore, QtGui
import sys
import datetime


app = QtGui.QApplication(sys.argv)

class ClientStatus(object) :
	__slots__ = (
		"server project platform client lastUpdate lastRun "+
		"failed failedTasks running runningTask "
		).split()
	def __init__(self, **args) :
		for key, value in args.iteritems() :
			setattr(self, key, value)


clients = [
	ClientStatus(
		server = "http://clam-project.org/testfarm",
		project = "CLAM",
		platform = "Ubuntu Natty",
		client = "Barcelona Media",
		lastUpdate = "2012-01-03 23:46:02",
		lastRun = "Passed",
		failed = True,
		failedTasks = "Compiling Network Editor",
		running = True,
		runningTask = "Compiling plugins",
		),
	ClientStatus(
		server = "http://clam-project.org/testfarm",
		project = "CLAM",
		platform = "Windows (crosscompiled)",
		client = "Barcelona Media",
		lastUpdate = "2012-02-03 23:46:02",
		lastRun = "Passed",
		failed = False,
		failedTasks = "Compiling Network Editor",
		running = True,
		runningTask = "Compiling plugins",
		),
	]

oldThresholdInHours = 20


class TestFarmIndicator(QtGui.QDialog) :
	def __init__(self) :
		super(TestFarmIndicator,self).__init__()
		self._greenIcon = QtGui.QIcon("images/testfarm.svg")
		self._redIcon = QtGui.QIcon("images/testfarm-burning.svg")
		self.setWindowIcon(self._greenIcon)
		self._tray = QtGui.QSystemTrayIcon(self._greenIcon,self)
		self._tray.activated.connect(self.showMe)
		self._tray.show()
		QtGui.QApplication.processEvents()

		trayMenu = QtGui.QMenu(self)
		trayMenu.setSeparatorsCollapsible(False)
		trayMenu.addAction(self._greenIcon, self.tr("Test Farm Indicator")).setSeparator(True)
		trayMenu.addAction(
			self.tr("Restore"),
			self.show,
			)
		trayMenu.addAction(
			QtGui.QIcon.fromTheme("preferences-system"),
			self.tr("Preferences"),
			self.show,
			)
		trayMenu.addSeparator()
		self._quitAction = trayMenu.addAction(
			QtGui.QIcon.fromTheme("application-exit"),
			self.tr("Quit"),
			QtGui.QApplication.instance().quit,
			)
		self._tray.setContextMenu(trayMenu)

		self.setLayout(QtGui.QVBoxLayout())
		self._statusLabel = QtGui.QLabel()
		self.layout().addWidget(self._statusLabel)
		self._list = QtGui.QListView()
		self.layout().addWidget(self._list)
		self._buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
		self._buttons.rejected.connect(self.reject)
		self._buttons.accepted.connect(self.accept)
		quitButton = self._buttons.addButton(self.tr("Quit"), QtGui.QDialogButtonBox.DestructiveRole)
		quitButton.clicked.connect(self._quitAction.trigger)
		quitButton.setIcon(QtGui.QIcon.fromTheme("application-exit"))
		self.layout().addWidget(self._buttons)

		self.updateSummary()

	def updateSummary(self) :

		nRed = len([client for client in clients if client.failed])
		nRunning = len([client for client in clients if client.running])
		oldDate = datetime.datetime.utcnow() - datetime.timedelta(hours=oldThresholdInHours)
		oldDateString = oldDate.strftime("%Y-%m-%d %H:%M:%S")
		nOld = len([client for client in clients if client.lastUpdate < oldDateString ])
		print [(client.lastUpdate,oldDateString) for client in clients ]

		toolTip = self.tr(
			"<img src='images/testfarm%0.svg' style='float: right'  width='64' />"
			"<h3>TestFarm Indicator</h3>"
		).arg("-burning" if nRed else "")
		if nRed != 0 : toolTip += self.tr(
			"<li><span style='color: red'>%0 clients failed!!</li>"
			).arg(nRed)
		if nOld != 0 : toolTip += self.tr(
			"<li><span style='color: darkred'>%0 clients down</li>"
			).arg(nOld)
		if nOld + nRed == 0 : toolTip += self.tr(
			"<li><span style='color: green'>%0 clients ok</li>"
			).arg(len(clients))
		if nRunning : toolTip += self.tr(
			"<li><span style='color: orange'>%0 clients running</li>"
			).arg(nRunning)
		if toolTip : toolTip += "<hr/>"
		for client in clients :
			toolTip +=  (self.tr(
				"<li><img source='images/%0'> <span style='color: %1'>Project: %2: Platform %3</span></li>")
				.arg("failed.png" if client.failed else "passed.png")
				.arg("red" if client.failed else "green")
				.arg(client.project)
				.arg(client.platform)
				)
		self._tray.setToolTip(toolTip)
		self._tray.setIcon(self._redIcon if nRed else self._greenIcon)

		self._statusLabel.setText(
			(self.tr("<li><span style='color: red'>%0 clients failed!!</li>").arg(nRed) if nRed else "") +
			(self.tr("<li><span style='color: darkred'>%0 clients down</li>").arg(nOld) if nOld else "") +
			(self.tr("<li><span style='color: green'>%0 clients ok</li>").arg(len(clients)) if nOld + nRed == 0 else "") +
			(self.tr("<li><span style='color: orange'>%0 clients running</li>").arg(nRunning) if nRunning else "")
			)

		clients[0].failed = not clients[0].failed
		QtCore.QTimer.singleShot(4000, self.updateSummary)


	def closeEvent(self, event) :
		# Just hide but do not quit the app
		self.hide()
		event.ignore()

	def showMe(self, reason) :
		if reason == QtGui.QSystemTrayIcon.Trigger :
			if self.isVisible() :
				self.hide()
			else :
				self.show()
		if reason == QtGui.QSystemTrayIcon.MiddleClick :
			pass
		if reason == QtGui.QSystemTrayIcon.Context :
			pass
		if reason == QtGui.QSystemTrayIcon.DoubleClick :
			self._tray.showMessage("Hey!","Tu",QtGui.QSystemTrayIcon.Critical,2000)




w = TestFarmIndicator()

app.exec_()



