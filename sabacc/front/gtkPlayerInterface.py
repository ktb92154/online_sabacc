#!/usr/bin/env python
# gtkPlayerInterface class
# Taken from SabaccApp version 0.5 (initial release)

from back.Interfaces import playerInterface

import threading, gobject

try:
	import pygtk
	pygtk.require('2.0')
except:
	pass
try:
	import gtk
except:
	sys.exit(1)
	
class gtkPlayerInterface (playerInterface):
	def __init__(self):
		self.window = gtk.Window()
		self.mainThread = threading.currentThread()
		self.active = False
		self.errors = False
		self.wait = False
	
	def writeError(self, text, title=None, parent=None):
		thread = threading.currentThread()
		if thread != self.mainThread:
			gobject.idle_add(self.writeError, text, title, parent)
			while self.wait:
				pass
			
		elif not self.errors:
			if title==None:
				title = text
			if parent==None:
				parent=self.window
			dialog = gtk.Dialog(title, parent, gtk.DIALOG_MODAL,
				(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
			dialog.connect("response", self.dialog_destroy)
			hbox = gtk.HBox()
			icon = gtk.Image()
			icon.set_from_stock(gtk.STOCK_DIALOG_ERROR, gtk.ICON_SIZE_DIALOG)
			label = gtk.Label(text)
			hbox.add(icon)
			hbox.add(label)
			dialog.vbox.pack_start(hbox, True, True, 0)
			dialog.show_all()
			if self.active:
				self.errors = True
				self.make_inactive()
			
			
	def dialog_destroy(self, dialog, response):
		if response == gtk.RESPONSE_ACCEPT: # error dialogs
			self.wait = False
		elif response == gtk.RESPONSE_OK: # 'next turn' dialogs
			self.thisPlay = True
			self.showCards(self.cards)
		dialog.destroy()
		
	def make_inactive(self):
		self.errors = False
		self.active = False
