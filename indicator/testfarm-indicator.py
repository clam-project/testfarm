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
import resources
import ast

app = QtGui.QApplication(sys.argv)

import urllib2

class ProjectListEditor(QtGui.QDialog) :
	def __init__(self, sources) :
		super(ProjectListEditor,self).__init__()
		self.setLayout(QtGui.QVBoxLayout())

		self.layout().addWidget(QtGui.QLabel("Tracked projects:"))
		self.sourceList = QtGui.QListWidget()
		self.sourceList.itemDoubleClicked.connect(self.editProject)

		self.layout().addWidget(self.sourceList)

		def newButton(text, icon, callback) :
			button = self._buttons.addButton( text, QtGui.QDialogButtonBox.ActionRole)
			button.setIcon(QtGui.QIcon.fromTheme(icon))
			button.clicked.connect(callback)
			return button

		self._buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
		self.layout().addWidget(self._buttons)
		self._buttons.rejected.connect(self.reject)
		self._buttons.accepted.connect(self.accept)
		newButton(self.tr("Add"), 'list-add', self.addProject)
		newButton(self.tr("Remove"), 'list-remove', self.removeProject)
		newButton(self.tr("Edit"), 'list-edit', self.editProject)

		self.sources = sources[:]
		self.reloadSources()

	def reloadSources(self) :
		self.sourceList.clear()
		def sourceItem(url, user=None, password=None) :
			icon = 'emblem-locked' if user or password else 'emblem-mounted'
			return QtGui.QListWidgetItem(QtGui.QIcon.fromTheme(icon), url)
		for source in self.sources :
			self.sourceList.addItem(sourceItem(*source))

	def editProject(self, item=None) :
		i = self.sourceList.row(item) if item else self.sourceList.currentRow()
		source = self.projectDialog("Editing a tracked project", *self.sources[i])
		if source is None : return
		self.sources[i]=source
		self.reloadSources()

	def removeProject(self) :
		i = self.sourceList.currentRow()
		del self.sources[i]
		self.reloadSources()

	def addProject(self) :
		source = self.projectDialog("Adding a new tracked project", "")
		if source is None : return
		self.sources.append(source)
		self.reloadSources()

	def projectDialog(self, title, url, user=None, password=None) :
		dialog = QtGui.QDialog()
		dialog.setWindowTitle(title)
		layout = QtGui.QFormLayout(dialog)
		urlEditor = QtGui.QLineEdit(url)
		urlEditor.setMinimumSize(urlEditor.minimumSize()+QtCore.QSize(400,0))
		layout.addRow("Project URL:", urlEditor)
		userEditor = QtGui.QLineEdit(user)
		layout.addRow("User (if needed):", userEditor)
		passwordEditor = QtGui.QLineEdit(password)
		passwordEditor.setEchoMode(QtGui.QLineEdit.Password)
		layout.addRow("Password (if needed):", passwordEditor)

		def check() :
			# TODO: Check that it works
			dialog.accept()

		buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
		buttons.rejected.connect(dialog.reject)
		buttons.accepted.connect(check)
		layout.addRow(buttons)
		if not dialog.exec_() : return None
		return str(urlEditor.text()), str(userEditor.text()) or None, str(passwordEditor.text()) or None

class ClientStatus(object) :
	__slots__ = (
		"server project platform client lastUpdate "+
		"status failedTasks doing runningTask "
		).split()
	def __init__(self, **args) :
		for key, value in args.iteritems() :
			setattr(self, key, value)
	def __str__(self) :
		return "(ClientStatus,\n"+"".join(["%s: %s\n"%(key, getattr(self,key)) for key in ClientStatus.__slots__])+")"
	def __repr__(self) :
		return str(self)


oldThresholdInHours = 20


class TestFarmIndicator(QtGui.QDialog) :
	def __init__(self) :
		super(TestFarmIndicator,self).__init__()
		self._greenIcon = QtGui.QIcon(":/images/testfarm.svg")
		self._redIcon = QtGui.QIcon(":/images/testfarm-burning.svg")
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
			self.showConfig,
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
#		self.layout().addWidget(self._statusLabel)
		infoScroll = QtGui.QScrollArea()
		self._info = QtGui.QLabel()
		self._info.setAlignment(QtCore.Qt.AlignTop)
		infoScroll.setWidgetResizable(True)
		infoScroll.setWidget(self._info)
		self.layout().addWidget(infoScroll)

		self._list = QtGui.QListView()
		infoScroll.setMinimumSize(700,50)
#		self.layout().addWidget(self._list)
		self._buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
		self._buttons.rejected.connect(self.reject)
		self._buttons.accepted.connect(self.accept)
		configButton = self._buttons.addButton( self.tr("Configure"), QtGui.QDialogButtonBox.ActionRole)
		configButton.setIcon(QtGui.QIcon.fromTheme('preferences-system'))
		configButton.clicked.connect(self.showConfig)
		quitButton = self._buttons.addButton(self.tr("Quit"), QtGui.QDialogButtonBox.DestructiveRole)
		quitButton.clicked.connect(self._quitAction.trigger)
		quitButton.setIcon(QtGui.QIcon.fromTheme("application-exit"))
		self.layout().addWidget(self._buttons)

		QtCore.QCoreApplication.setOrganizationName("clam-project")
		QtCore.QCoreApplication.setOrganizationDomain("clam-project.org")
		QtCore.QCoreApplication.setApplicationName("TestFarmIndicator")

		self.loadSources()

		self.reloadData()

	def getUrl(self, url, username=None, password=None) :
		if username :
			passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
			passman.add_password(None, url, username, password)

			authhandler = urllib2.HTTPBasicAuthHandler(passman)
			opener = urllib2.build_opener(authhandler)
			urllib2.install_opener(opener)

		return urllib2.urlopen(url+"/testfarm-data.js").read()

	def saveSources(self) :
		def saveSource(settings, url, user=None, password=None) :
			settings.setValue("url", url)
			if user : settings.setValue("username", user)
			if password: settings.setValue("password", password)
		settings = QtCore.QSettings()
		settings.beginWriteArray("sources")
		for i, source in enumerate(self.sources) :
			settings.setArrayIndex(i)
			saveSource(settings, *source)
		settings.endArray()

	def loadSources(self) :
		self.sources = []
		settings = QtCore.QSettings()
		n = settings.beginReadArray("sources")
		for i in xrange(n) :
			settings.setArrayIndex(i)
			source = [
				str(settings.value(key).toString())
				for key in ["url", "username", "password"]
				if key in settings.childKeys() ]
			self.sources.append(source)
		settings.endArray()

	def reloadData(self) :
		clients = []
		for source in self.sources :
			jsonData = self.getUrl(*source)
			data = ast.literal_eval(jsonData)
			server = source[0]
			project = data['project']
			for client in data['clients'] :
				clientStatus = ClientStatus(
					server = server,
					project = project,
					platform = "TODO",
					client = client['name'],
					lastUpdate = client['lastupdate'],
					status = client['status'],
					failedTasks = client['failedTasks'] if 'failedTasks' in client else [],
					doing = client['doing'],
					runningTask = client['currentTask'] if 'currentTask' in client else '',
					)
				clients.append(clientStatus)
		print clients
		self.updateSummary(clients)
		# TODO: if sensitiveInfo(clients) != sensitiveInfo(self.clients) : notifyChange()
		self.clients = clients


	def updateSummary(self, clients) :
		nRed = len([client for client in clients if client.status == 'red'])
		nRunning = len([client for client in clients if client.doing == 'run'])
		oldDate = datetime.datetime.utcnow() - datetime.timedelta(hours=oldThresholdInHours)
		oldDateString = oldDate.strftime("%Y-%m-%d %H:%M:%S")
		nOld = len([client for client in clients if client.doing=='old' or client.lastUpdate < oldDateString ])
		print [(client.lastUpdate,oldDateString) for client in clients ]

		toolTip = self.tr(
			"<img src=':/images/testfarm%0.svg' style='float: right'  width='64' />"
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
				"<li><img source=':/images/%0'> <span style='color: %1'>Project: %2: Client: %3</span></li>")
				.arg("failed.png" if client.status == 'red' else "passed.png")
				.arg("red" if client.status == 'red' else "green")
				.arg(client.project)
				.arg(client.client)
				)
		self._tray.setToolTip(toolTip)
		self._tray.setIcon(self._redIcon if nRed else self._greenIcon)

		self._statusLabel.setText(
			(self.tr("<li><span style='color: red'>%0 clients failed!!</li>").arg(nRed) if nRed else "") +
			(self.tr("<li><span style='color: darkred'>%0 clients down</li>").arg(nOld) if nOld else "") +
			(self.tr("<li><span style='color: green'>%0 clients ok</li>").arg(len(clients)) if nOld + nRed == 0 else "") +
			(self.tr("<li><span style='color: orange'>%0 clients running</li>").arg(nRunning) if nRunning else "")
			)
		self._info.setText(toolTip)

		QtCore.QTimer.singleShot(4000, self.reloadData)


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

	def showConfig(self) :
		dialog = ProjectListEditor(self.sources)
		dialog.setWindowTitle("TestFarm Indicator Preferences")
		if not dialog.exec_() : return
		self.sources = dialog.sources
		self.saveSources()
		self.reloadData()


w = TestFarmIndicator()
app.setQuitOnLastWindowClosed(False);
app.exec_()



