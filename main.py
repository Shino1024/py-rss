import urllib2
from xml.dom import minidom
from gi.repository import Gtk

class ErrorDialog(Gtk.Dialog):
	def __init__(self, parent, errorMessage):
		Gtk.Dialog.__init__(self, "Error", parent, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK))
		
		self.set_default_size(120, 80)
		infoLabel = Gtk.Label(errorMessage)
		area = self.get_content_area()
		box.add(infoLabel)

		self.show_all()

class MainWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="PyRSS")

		self.resultsTitle = []
		self.resultsItems = []

		self.connect("destroy", Gtk.main_quit)

		self.addressBar = Gtk.Entry()
		self.addressBar.set_input_purpose(Gtk.InputPurpose.URL)
		self.addressBar.set_width_chars(64)
		self.searchButton = Gtk.Button()
		self.searchButton.set_text("Search")
		self.searchButton.set_size_request(40, 30)
		self.searchButton.connect("clicked", self.parseRequest)

		self.results = Gtk.ScrolledWindow()
		self.titleVBox = Gtk.VBox()
		self.titleFrame = Gtk.Frame()
		self.titleElements = []
		self.itemsVBox = Gtk.VBox()
		self.itemsFrame = Gtk.Frame()
		self.items = []

		self.results.add(layout)
		self.results.set_vexpand(True)
		self.results.set_hexpand(True)

		self.mainGrid = Gtk.Grid()
		self.mainGrid.attach(self.addressBar, 0, 0, 1, 1)
		self.mainGrid.attach(self.searchButton, 1, 0, 1, 1)
		self.mainGrid.attach(self.results, 0, 1, 2, 1)

		self.add(self.mainGrid)
		self.set_default_size(-1, -1)

		self.mainWindow.show_all()

	def parserequest(self, button):
		button.set_text("Parsing...")
		address = self.addressBar.get_text()
		request = urllib2.Request(address)

		try:
			data = urllib2.urlopen(request)
		except urllib2.URLError as e:
			button.set_text("Error!")
			if e.reason[0] == 4:
				ErrorDialog(self, "Unknown host, have you mispelled it?").run()
			else:
				ErrorDialog(self, e.reason[1]).run()
			return

		doc = minidom.parseString(data.read())
		root = doc.childNodes

		tags = ["copyright", "description", "generator", "language", "lastBuildDate", "link", "pubDate", "title"]
		for node in tags:
			temp = doc.getElementsByTagName(node)
			if len(temp) == 0:
				self.resultsTitle.append(None)
				continue
			for elem in temp:
				if elem.parentNode.nodeName == "channel":
					self.resultsTitle.append(elem.firstChild.nodeValue)

		items = doc.getElementsByTagName("item")
		if len(items) == 0:
			return
		itemTags = ["author", "category", "comments", "description", "link", "pubDate", "title"]
		for item in items:
			itemData = []
			for info in itemTags:
				temp = item.getElementsByTagName(info)
				if len(temp) == 0:
					itemData.append(None)
					continue
				for elem in temp:
					itemData.append(elem.firstChild.nodeValue)
				self.resultsItems.append(itemData)

		button.set_text("Search")
		refillContainer()

	def refillContainer(self):
		for item in self.items:
			self.itemsVBox.remove(item)
		for item in self.titleElements:
			self.titleVBox.remove(item)
