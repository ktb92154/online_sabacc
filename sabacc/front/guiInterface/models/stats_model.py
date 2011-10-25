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
stats_model.py (taken from Sabacc version 1.0-beta1)
This module contains the model for the individual 'agent data' windows.
"""

from gtkmvc import Model

class StatsModel (Model):
	'''
	This class contains the model for the stats window.
	'''
	# Observable properties
	__properties__ = dict(	player_controller=None, # controller for the player window
						agent=None # the agent whose stats we're showing
	)
	
	def __init__(self, player_controller):
		Model.__init__(self)
		self.player_controller = player_controller
		self.agent = player_controller.model.agent
		return
	
	pass # end of class StatsModel
