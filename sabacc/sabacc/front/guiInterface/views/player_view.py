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
player_view.py (rewrite of front.wndPlayer from 0.6 'Ackbar')
This module contains the view for the individual player windows.
"""

from gtkmvc import View
import gtk

class PlayerView (View):
	'''
	This class contains the view for the player window.
	'''
	def __init__(self, ctrl):
		from front import gladefile#!
		View.__init__(self, ctrl, gladefile,
			"player_window", register=False)
		self.setup_widgets()
		ctrl.register_view(self)
		return

	def setup_widgets(self):
		'''Deals with construction of manual widgets and other
		settings.'''
		
		from front import iconpath#!
		self['player_window'].set_icon_from_file(iconpath)
		return

	pass # end of class PlayerView
