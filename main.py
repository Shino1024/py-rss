import urllib as ul
from xml.dom import minidom
from gi.repository import Gtk

class MainWindow():
	def __init__(self):
		self.initialize()

	def initialize(self):
		self.resultsTitle = []
		self.resultsItems = []

		self.mainWindow = Gtk.Window()
		self.mainWindow.connect("destroy", Gtk.main_quit)

		self.addressBar = Gtk.Entry()
		self.addressBar.set_input_purpose(Gtk.InputPurpose.URL)
		self.searchButton = Gtk.Button()
		self.searchButton.set_text("Search")
		self.seatchButton.set_size_request(40, 30)
		self.searchButton.connect("clicked", self.parseRequest)
		self.results = Gtk.ListBox()

		self.mainGrid = Gtk.Grid()
		self.mainGrid.attach(self.addressBar, 0, 0, 1, 1)
		self.mainGrid.attach(self.searchButton, 1, 0, 1, 1)
		self.mainGrid.attach(self.results, 0, 1, 1, 1)

		self.mainWindow.add(self.mainGrid)
		self.mainWindow.set_default_size(400, 400)
		self.mainWindow.set_resizable(False)

		self.mainWindow.show_all()

	def parserequest(self, button):
		button.set_text("Parsing...")
		address = self.addressBar.get_text()
		request = urllib2.Request(address)
		try:
			data = urllib2.urlopen(request)
		except URLError as e:
			button.set_text("Error!")
			if e.reason[0] == 4:
				Gtk.MessageDialog(type=Gtk.MESSAGE_ERROR, buttons=Gtk.BUTTONS_OK).set_markup("Can't reach the server.").run()
			else:
				Gtk.MessageDialog(type=Gtk.MESSAGE_ERROR, buttons=Gtk.BUTTONS_OK).set_markup(e.reason[1]).run()
		doc = minidom.parseString(data)
		root = doc.childNodes
		datatable = []
		tags = ["title", "description", "link", "pubDate", "image", "generator", "copyright", "lastBuildDate", "language"]
		for node in tags:
			temp = doc.getElementsByTagName(node)
			if len(temp) == 0:
				self.resultsTitle.append(None)
				continue
			for elem in temp:
				if elem.nodeType == elem.TEXT_NODE and elem.parentNode.nodeName == "channel":
					self.resultsTitle.append(elem.firstChild.nodeValue)
		items = doc.getElementsByTagName("item")
#		if len(items) == 0:
		else:
			itemTags = ["author", "category", "comments", "description", "link", "pubDate", "title"]
			for item in items:
				itemData = []
				for info in item.childNodes:
					temp = item.getElementsByTagName(info)
					if len(temp) == 0:
						itemData.append(None)
						continue
					for elem in temp:
						if elem.nodeType == elem.TEXT_NODE:
							itemData.append(elem.firstChild.nodeValue)
					self.resultsItems.append(itemData)
		button.set_text("Search")

	def represent(self):