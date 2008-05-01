# Sabacc -- an interesting card game similar to Blackjack.
# Copyright (C) 2007-2008 Joel Cross.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""
gtkPlayerInterface.py (taken from version 0.6 'Ackbar')
This module contains the gtkPlayerInterface class.
"""

from sabacc.back.Interfaces import playerInterface

import threading, gobject, gtk, gtk.glade
	
class gtkPlayerInterface (playerInterface):
	"""
	This is an abstract class that can be used by any GTK
	extension of the playerInterface class.
	"""
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
