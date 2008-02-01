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
HumanAgent.py (taken from version 0.6beta1)
This module contains the HumanAgent class.
"""

# import base class
from Agent import Agent

class HumanAgent (Agent):
	"""
	This is a dummy class whose methods all point
	to various methods in its interface.
	"""
	def move(self, cards):
		move = self.interface.getMove(cards)
		return move
		
	def bet(self, cards, mustMatch):
		bet = self.interface.getBet(cards, mustMatch)
		return bet
		
	def gameOver(self, won, cards):
		self.interface.gameStatus(won, cards, self.credits)
		return 0
