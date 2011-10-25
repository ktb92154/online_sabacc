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
game_model.py (taken from Sabacc version 1.0-beta1)
This module contains the model for the main game window.
"""

from gtkmvc import Model

class GameModel (Model):
	'''
	This class contains the model for the main game window.
	'''
	
	# Observable properties
	__properties__ = dict(
		humans_in_game=0,
		num_players=0,
		hand_pot=0, # value of hand pot
		sabacc_pot=0, # value of Sabacc pot
		last_ante=5, # what was the previous initial ante?
		messages='' # contents of message label
	)
	
	def __init__(self):
		Model.__init__(self)
	
	pass # end of class GameModel
