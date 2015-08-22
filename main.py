import urllib2
from xml.dom import minidom
from gi.repository import Gtk, Pango, Gdk
from xml.etree import ElementTree

class ErrorDialog(Gtk.Dialog):
	def __init__(self, parent, errorMessage):
		Gtk.Dialog.__init__(self, "Error", parent, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK))
		
		self.set_default_size(120, 80)
		infoLabel = Gtk.Label()
		infoLabel.modify_font(Pango.FontDescription("Arial 12"))
		infoLabel.set_markup("<b>" + errorMessage + "</b>")
		infoLabel.set_padding(4, 2)
		area = self.get_content_area()
		area.add(infoLabel)

		self.show_all()

class MainWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="PyRSS")
		self.set_icon_from_file("rss.png")

		self.resultsChannel = []
		self.resultsItems = []

		self.connect("destroy", Gtk.main_quit)

		self.addressBar = Gtk.Entry()
		self.addressBar.set_hexpand(True)
		self.addressBar.set_input_purpose(Gtk.InputPurpose.URL)
		self.addressBar.set_text("Provide the URL here...")

		self.buttonBox = Gtk.VBox()
		self.parseButton = Gtk.Button()
		self.parseButton.set_label("Parse")
		self.parseButton.connect("clicked", self.parseRequest)
		self.buttonBox.pack_start(self.parseButton, False, False, False)

		self.results = Gtk.ScrolledWindow(vexpand=True)
		self.resultsBox = Gtk.Box()
		self.results.add(self.resultsBox)
		self.resultsVBox = Gtk.VBox()
		self.resultsBox.pack_start(self.resultsVBox, True, True, False)

		self.mainGrid = Gtk.Grid()
		self.mainGrid.attach(self.addressBar, 0, 0, 1, 1)
		self.mainGrid.attach(self.buttonBox, 1, 0, 1, 1)
		self.mainGrid.attach(self.results, 0, 1, 2, 1)

		self.add(self.mainGrid)
		self.resize(512, 640)

		self.show_all()

	def parseRequest(self, button):
		button.set_label("Parsing...")
		address = self.addressBar.get_text()
		request = urllib2.Request(address)

		try:
			data = urllib2.urlopen(request)
		except ValueError:
			button.set_label("Parse")
			dialog = ErrorDialog(self, "The address seems to be wrong.")
			dialog.run()
			dialog.destroy()
			return
		except urllib2.URLError as e:
			button.set_label("Parse")
			if e.reason[0] == 4:
				dialog = ErrorDialog(self, "Unknown host, have you mispelled it?")
				dialog.run()
				dialog.destroy()
			else:
				dialog = ErrorDialog(self, e.reason[1])
				dialog.run()
				dialog.destroy()
			return

		doc = minidom.parseString(data.read())

		tags = ["title", "link", "lastBuildDate", "description"]
		for node in tags:
			temp = doc.getElementsByTagName(node)
			if len(temp) == 0:
				self.resultsChannel.append(":NONE")
				continue
			for elem in temp:
				if elem.parentNode.nodeName == "channel":
					self.resultsChannel.append(''.join(ElementTree.fromstring(elem.firstChild.nodeValue.replace("<br>", "\n").replace("</br>", "\n").replace("</ br>", "\n").replace("&lt;", "<").replace("&gt;", ">"))).itertext())

		items = doc.getElementsByTagName("item")
		if len(items) == 0:
			return
		itemTags = ["title", "link", "pubDate", "description", "author", "category"]
		for item in items:
			itemData = []
			for info in itemTags:
				temp = item.getElementsByTagName(info)
				if len(temp) == 0:
					itemData.append(":NONE")
					continue
				for elem in temp:
					itemData.append(''.join(ElementTree.fromstring(elem.firstChild.nodeValue.replace("<br>", "\n").replace("</br>", "\n").replace("</ br>", "\n").replace("&lt;", "<").replace("&gt;", ">"))).itertext())
			self.resultsItems.append(itemData)

		button.set_label("Parse")
		self.refillContainer()

	def refillContainer(self):
		self.resultsBox.remove(self.resultsVBox)
		self.resultsVBox = Gtk.VBox()
		self.resultsVBox.set_spacing(5)

		channelBox = Gtk.HBox()
		channelDummyL, channelDummyR = Gtk.Label(), Gtk.Label()
		channelBox.pack_start(channelDummyL, False, False, False)
		channelDummyL.show()
		channelBox.set_spacing(5)

		channelFrame = Gtk.Frame()
		channelFrame.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.9, .9, .9, 1.0))
		channelLabel = Gtk.Label()
		channelLabel.set_markup("<b>Channel</b>")
		channelLabel.modify_font(Pango.FontDescription("Times New Roman 8"))
		channelLabel.show()
		channelFrame.set_label_align(0.01, 0.8)
		channelFrame.set_label_widget(channelLabel)
		channelFrameBox = Gtk.VBox()
		channelFrame.add(channelFrameBox)
		channelFrameBox.show()

		channelHeaderBox = Gtk.HBox()

		channelTitle = Gtk.Label()
		channelTitle.modify_font(Pango.FontDescription("Arial 10"))
		channelTitle.set_padding(4, 2)
		channelTitle.set_selectable(True)
		channelTitle.set_alignment(0, 0)
		channelTitle.set_line_wrap(True)
		channelTitle.set_single_line_mode(False)
		if self.resultsChannel[0] != ":NONE":
			if self.resultsChannel[1] != ":NONE":
				channelTitle.set_markup("<a href=\"" + self.resultsChannel[1].replace("&", "&amp;") + "\">" + self.resultsChannel[0] + "</a>")
			else:
				channelTitle.set_text(self.resultsChannel[0])
		elif self.resultsChannel[1] != ":NONE":
			channelTitle.set_markup("<a href=\"" + self.resultsChannel[1].replace("&", "&amp;") + "\">Link to the source</a>")
		else:
			channelTitle.set_text("Untitled")

		channelHeaderSeparator = Gtk.Separator()
		channelHeaderSeparator.set_orientation(Gtk.Orientation.VERTICAL)

		channelDate = Gtk.Label()
		channelDate.modify_font(Pango.FontDescription("Arial 10"))
		channelDate.set_padding(4, 2)
		channelDate.set_selectable(True)
		channelDate.set_alignment(0, 0)
		channelDate.set_line_wrap(True)
		channelDate.set_single_line_mode(False)
		if self.resultsChannel[2] != ":NONE":
			channelDate.set_text(self.resultsChannel[2])
		else:
			channelDate.set_text("Unknown date")

		channelDescriptionSeparator = Gtk.Separator()
		channelDescription = Gtk.Label()
		channelDescription.modify_font(Pango.FontDescription("Arial 10"))
		channelDescription.set_padding(4, 2)
		channelDescription.set_selectable(True)
		channelDescription.set_alignment(0, 0)
		channelDescription.set_line_wrap(True)
		channelDescription.set_single_line_mode(False)
		if self.resultsChannel[3] != ":NONE":
			channelDescription.set_text(self.resultsChannel[3])
		else:
			channelDescription.set_text("<i>No description available.</i>")

		channelHeaderBox.pack_start(channelTitle, False, False, False)
		channelTitle.show()
		channelHeaderBox.pack_end(channelDate, False, False, False)
		channelDate.show()
		channelHeaderBox.pack_end(channelHeaderSeparator, False, False, False)
		channelHeaderSeparator.show()

		channelBox.pack_start(channelFrame, True, True, False)
		channelFrame.show()
		channelBox.pack_start(channelDummyR, False, False, False)
		channelDummyR.show()

		channelFrameBox.pack_start(channelHeaderBox, True, True, False)
		channelHeaderBox.show()
		channelFrameBox.pack_start(channelDescriptionSeparator, False, False, False)
		channelDescriptionSeparator.show()
		channelFrameBox.pack_start(channelDescription, False, False, False)
		channelDescription.show()

		self.resultsVBox.pack_start(channelBox, True, True, False)
		channelBox.show()

		counter = 1
		for item in self.resultsItems:
			itemBox = Gtk.HBox()
			itemDummyL, itemDummyR = Gtk.Label(), Gtk.Label()
			itemBox.pack_start(itemDummyL, False, False, False)
			itemDummyL.show()
			itemBox.set_spacing(5)

			itemFrame = Gtk.Frame()
			itemFrame.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(1.0, 1.0, 1.0, 1.0))
			itemLabel = Gtk.Label()
			itemLabel.set_markup("<i>Entry " + str(counter) + "</i>")
			counter += 1
			itemLabel.modify_font(Pango.FontDescription("Times New Roman 8"))
			itemLabel.show()
			itemFrame.set_label_align(0.01, 0.8)
			itemFrame.set_label_widget(itemLabel)
			itemFrameBox = Gtk.VBox()
			itemFrame.add(itemFrameBox)
			itemFrameBox.show()

			itemHeaderBox = Gtk.HBox()

			itemTitle = Gtk.Label()
			itemTitle.modify_font(Pango.FontDescription("Arial 10"))
			itemTitle.set_padding(4, 2)
			itemTitle.set_selectable(True)
			itemTitle.set_alignment(0, 0)
			itemTitle.set_line_wrap(True)
			itemTitle.set_single_line_mode(False)
			if item[0] != ":NONE":
				if item[1] != ":NONE":
					itemTitle.set_markup("<a href=\"" + item[1].replace("&", "&amp;") + "\">" + item[0] + "</a>")
				else:
					itemTitle.set_text(item[0])
			elif self.resultsChannel[1] != ":NONE":
				itemTitle.set_markup("<a href=\"" + item[1].replace("&", "&amp;") + "\">Link to the source</a>")
			else:
				itemTitle.set_text("Untitled")

			itemHeaderSeparator = Gtk.Separator()
			itemHeaderSeparator.set_orientation(Gtk.Orientation.VERTICAL)

			itemDate = Gtk.Label()
			itemDate.modify_font(Pango.FontDescription("Arial 10"))
			itemDate.set_padding(4, 2)
			itemDate.set_selectable(True)
			itemDate.set_alignment(0, 0)
			itemDate.set_line_wrap(True)
			itemDate.set_single_line_mode(False)
			if item[2] != ":NONE":
				itemDate.set_text(item[2])
			else:
				itemDate.set_text("Unknown date")

			itemDescriptionSeparator = Gtk.Separator()
			itemDescription = Gtk.Label()
			itemDescription.modify_font(Pango.FontDescription("Arial 10"))
			itemDescription.set_padding(4, 2)
			itemDescription.set_selectable(True)
			itemDescription.set_alignment(0, 0)
			itemDescription.set_line_wrap(True)
			itemDescription.set_single_line_mode(False)
			if item[3] != ":NONE":
				itemDescription.set_text(item[3])
			else:
				itemDescription.set_text("<i>No description available.</i>")

			itemFooterBox = Gtk.HBox()
			itemDescriptionSeparator2 = Gtk.Separator()

			itemAuthor = Gtk.Label()
			itemAuthor.modify_font(Pango.FontDescription("Arial 10"))
			itemAuthor.set_padding(4, 2)
			itemAuthor.set_selectable(True)
			itemAuthor.set_alignment(0, 0)
			itemAuthor.set_line_wrap(True)
			itemAuthor.set_single_line_mode(False)
			if item[4] != ":NONE":
				itemAuthor.set_text(item[4])
			else:
				itemAuthor.set_text("Unknown author")

			itemFooterSeparator = Gtk.Separator()
			itemFooterSeparator.set_orientation(Gtk.Orientation.VERTICAL)

			itemCategory = Gtk.Label()
			itemCategory.modify_font(Pango.FontDescription("Arial 10"))
			itemCategory.set_padding(4, 2)
			itemCategory.set_selectable(True)
			itemCategory.set_alignment(0, 0)
			itemCategory.set_line_wrap(True)
			itemCategory.set_single_line_mode(False)
			if item[5] != ":NONE":
				itemCategory.set_text(item[5])
			else:
				itemCategory.set_text("Unknown category")

			itemHeaderBox.pack_start(itemTitle, False, False, False)
			itemTitle.show()
			itemHeaderBox.pack_end(itemDate, False, False, False)
			itemDate.show()
			itemHeaderBox.pack_end(itemHeaderSeparator, False, False, False)
			itemHeaderSeparator.show()

			itemFooterBox.pack_start(itemAuthor, False, False, False)
			itemAuthor.show()
			itemFooterBox.pack_end(itemCategory, False, False, False)
			itemCategory.show()
			itemFooterBox.pack_end(itemFooterSeparator, False, False, False)
			itemFooterSeparator.show()

			itemBox.pack_start(itemFrame, True, True, False)
			itemFrame.show()
			itemBox.pack_start(itemDummyR, False, False, False)
			itemDummyR.show()

			itemFrameBox.pack_start(itemHeaderBox, True, True, False)
			itemHeaderBox.show()
			itemFrameBox.pack_start(itemDescriptionSeparator, False, False, False)
			itemDescriptionSeparator.show()
			itemFrameBox.pack_start(itemDescription, False, False, False)
			itemDescription.show()
			itemFrameBox.pack_start(itemDescriptionSeparator2, False, False, False)
			itemDescriptionSeparator2.show()
			itemFrameBox.pack_start(itemFooterBox, True, True, False)
			itemFooterBox.show()

			self.resultsVBox.pack_start(itemBox, True, True, False)
			itemBox.show()

		self.resultsBox.pack_start(self.resultsVBox, True, True, False)
		self.resultsVBox.show()

		self.resultsItems = []
		self.resultsChannel = []

if __name__ == "__main__":
	RSS = MainWindow()
	Gtk.main()