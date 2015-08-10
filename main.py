import urllib as ul
from xml.dom import minidom
from gi.repository import Gtk

class MainWindow():
	def __init__(self):
		self.initialize()

	def initialize(self):
		self.doc = None

		self.window = Gtk.Window()
		self.window.connect("destroy", Gtk.main_quit)

		self.addressbar = Gtk.Entry()
		self.addressbar.set_input_purpose(Gtk.InputPurpose.URL)
		self.searchbutton = Gtk.Button()
		self.searchbutton.set_text("Search")
		self.searchbutton.connect("clicked", self.parserequest)
		self.results = Gtk.ListBox()

		self.maingrid = Gtk.Grid()
		self.maingrid.attach(self.addressbar, 0, 0, 1, 1)
		self.maingrid.attach(self.searchbutton, 1, 0, 1, 1)
		self.maingrid.attach(self.results, 0, 1, 1, 1)

		self.window.add(self.maingrid)
		self.window.set_default_size(400, 400)
		self.window.set_resizable(False)

		self.window.show_all()

	def parserequest(self, button):
		address = self.addressbar.get_text()
		request = urllib2.Request(address)
		try:
			data = urllib2.urlopen(request)
		except URLError as e:
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
			