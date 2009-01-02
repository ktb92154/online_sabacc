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
stats_view.py (partial rewrite of front.wndTrain from 0.6 'Ackbar')
This module contains the view for the individual 'agent data' windows.
"""

from common import ThreadSafeView
import gtk

class StatsView (ThreadSafeView):
	'''
	This class contains the view for the stats window.
	'''
	def __init__(self, ctrl):
		from sabacc.constants import glade_filename
		ThreadSafeView.__init__(self, ctrl, glade_filename,
			"stats_window", register=False)
		self.setup_widgets()
		ctrl.register_view(self)
		return
	
	def setup_widgets(self):
		'''Deals with construction of manual widgets and other
		settings.'''
		
		from sabacc.constants import icon_filename
		
		gtk.gdk.threads_enter()
		self['stats_window'].set_icon_from_file(icon_filename)
		gtk.gdk.threads_leave()
