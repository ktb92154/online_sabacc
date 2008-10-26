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
game_view.py (rewrite of front.wndGame from 0.6 'Ackbar')
This module contains the view for the main game window.
"""

from gtkmvc import View

import gtk
import os.path

class GameView (View):
	'''
	This class contains the view for the main game window.
	'''
	def __init__(self, ctrl):
		from sabacc.constants import glade_filename
		View.__init__(self, ctrl, glade_filename,
			"game_window", register=False)
		self.setup_widgets()
		
		ctrl.register_view(self)

	def setup_widgets(self):
		'''Deals with construction of manual widgets and other
		settings.'''
		
		from sabacc.constants import icon_filename
		self['game_window'].set_icon_from_file(icon_filename)
		
		# Create object for displaying messages
		message_label = gtk.Label()
		message_label.set_alignment(0.0,0.0)
		
		self['message_space'].add_with_viewport(message_label)
		message_label.show()
		self['message_label'] = message_label
		
		# Create 'add computer' menu
		self['computer_button_menu'] = gtk.Menu()
		self['new_agent_menu'] = gtk.MenuItem('Create a new agent')
		self['load_agent_menu'] = gtk.MenuItem('Load an existing agent')
		
		for menu_item in (self['new_agent_menu'], self['load_agent_menu']):
			self['computer_button_menu'].append(menu_item)
			menu_item.show()
		
		self['computer_button_menu'].show()
		
		#Move window to bottom of screen and resize
		width, height = self['game_window'].get_size()
		new_width=gtk.gdk.screen_width()
		
		# Make sure screen isn't too wide on Windows dual-display
		if new_width >= gtk.gdk.screen_height() * 2:
			newwidth /= 2
		
		new_height = height+100
		self['game_window'].resize(new_width, new_height)
		self['game_window'].move(0, gtk.gdk.screen_height() - new_height)
		self['game_window'].show()

	pass # end of class GameView
