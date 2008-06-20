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
player_model.py (rewrite of front.wndPlayer from 0.6 'Ackbar')
This module contains the model for the individual player windows.
"""

from gtkmvc import Model

class PlayerModel (Model):
	'''
	This class contains the model for the player window.
	'''
	
	# Observable properties
	statuses = dict(begin=0, in_game=1, end=2) # possible statuses
	
	__properties__ = dict(name=None, # player name
		is_human=None,
		game_controller=None, # controller for the game window
		agent=None, # agent object
		status=statuses['begin'], # 'status' displayed in window
		credits=0,
		cards=[],
		this_human_in_play=False,#	if >1 human this is used to hide
							#	their cards from each other
		last_shown_cards=[], #	prevents having to show the same
						#	cards over and over
		active=False # is this player currently in the game?
	)
	
	def __init__(self, game_controller, name, is_human):
		Model.__init__(self)
		self.game_controller = game_controller
		self.name = name
		self.is_human = is_human
		
		if is_human:
			self.this_human_in_play = True
		
		# Get agent object
		from sabacc.back import Game
		if name in Game.names:
			index = Game.names.index(name)
			self.agent = Game.loaded[index][0]
		else:
			sys.stderr.write('Error: Agent \'%s\' not found in game!\n' %name)
		
		return
	
	pass # end of class PlayerModel
