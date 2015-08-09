import urllib as ul
import xml.etree.ElementTree as ETree
from gi.repository import Gtk

class MainWindow():
	def __init__(self):
		self.initialize()

	def initialize(self):
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

		self.rssdoc = ETree.ElementTree()

		self.urlobj = None

	def parserequest(self, button):
		self.address = self.addressbar.get_text()
		self.request = urllib.open(self.address)