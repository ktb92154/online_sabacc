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
player_ctrl.py (rewrite of front.wndPlayer from 0.6 'Ackbar')
This module contains the controller for the individual player windows.
"""

from gtkmvc import Controller
from gtkmvc import adapters
import gtk

class PlayerCtrl (Controller):
	'''
	This class contains the controller for the player window,
	which shows one particular agent's status in the game.
	'''
	def __init__(self, model):
		Controller.__init__(self, model)
		model.agent.interface.controller = self
		return
	
	def register_view(self, view):
		'''Sets up the view and handles widget signals.'''
		Controller.register_view(self, view)
		
		# setup of widgets
		self.view['player_window'].set_title(self.model.name)
		self.view['player_window'].connect('delete-event', self.window_close)
		
		if self.model.is_human:
			self.view['betspinner'].show()
			self.view['move1_button'].set_label("End betting")
			self.view['move2_button'].set_label("Leave game")
			self.view['move3_button'].set_label("Call the hand")
		else:
			self.view['move1_button'].hide()
			self.view['move2_button'].hide()
			self.view['move3_button'].hide()
		
		self.update_cards()
		self.view['player_window'].show()
		return

	def register_adapters(self):
		# setup of adapters
		self.update_labels()
		return

	# Handlers for signals:
	def window_close(self, win, event):
		'''Handler for window close event. Prepares to remove
		player from game.'''
		if self.model.active:
			self.model.agent.quit_next_turn = True
			if self.model.agent.interface.wait:
				from sabacc.back.settings import moves#!
				self.model.agent.interface.chosen_move = moves['fold']
				self.model.agent.interface.wait = False
		
		final = self.model.game_controller.remove_player(self.model.name, self.model.active)
		return not final
	
	def update_cards(self, show_all_cards=False):
		'''Shows the given cards to the user.'''
		
		cards = self.model.cards[:]
		
		# Show backs of cards if empty hand
		if cards == []:
			cards=[-1, -1]
		
		# Always show current player's hand
		if self.model.this_human_in_play:
			show_all_cards = True
		
		# If cards are hidden, show backs
		if not show_all_cards:
			for index in range(len(cards)):
				cards[index] = -1
		
		# only show cards if a change has happened
		if cards == self.model.last_shown_cards:
			return
		self.model.last_shown_cards = cards
		
		# If we've got loads of cards, we need to make them smaller
		smallcards = False
		
		if len(cards) <= 5: # 5 cards per row
			rows = 2 # 1 row, picture and text
			columns = len(cards)
		elif len(cards) <= 10:
			rows = 4 # 2 rows, picture and text
			columns = (len(cards) / 2 + len(cards) % 2)
		else:
			smallcards = True
			if len(cards) % 8 >= 1:
				mod = 1
			else:
				mod = 0
			rows = len(cards) / 8 + mod
			columns = 8
		
		# remove current cards from table
		for card in self.view['card_layout'].get_children():
			self.view['card_layout'].remove(card)
		
		self.view['card_layout'].resize(rows, columns)
		
		card_index = 0
		score = 0
		score_unknown = False
		idiot_cards = [False, False, False]
		
		from front import basedir, sharedir#!
		from front.settings import CARDSET, CARDIMAGES#!
		from back.settings import CARDNAMES, CARDVALUE#!
		import os.path
		
		cardsdir = os.path.join(basedir, "cardsets", CARDSET)#!
		if not os.path.exists(cardsdir):
			cardsdir = os.path.join(sharedir, "sabacc", "cardsets", CARDSET)#!
			if not os.path.exists(cardsdir):
				self.model.agent.interface.write_error("Warning: Cardset '%s' not found!" %CARDSET)
		
		for row in range(rows):
			for col in range(columns):
				if not smallcards and row % 2 == 1: # odd rows
					break
				try:
					im = gtk.Image()
					
					filename = os.path.join(cardsdir, CARDIMAGES[cards[card_index]])
					if smallcards:
						# Scale card image
						im.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(
							filename).scale_simple(62, 89,
							gtk.gdk.INTERP_BILINEAR))
					else:
						im.set_from_file(filename)
					self.view['card_layout'].attach(im, col,col+1,row,row+1)
					im.show()
					if not smallcards:
						if cards[card_index] == -1:
							text = "Unknown card"
						else:
							text = '%s (value %i)' \
								%(CARDNAMES[cards[card_index]],
								CARDVALUE[cards[card_index]])
						lbl = gtk.Label(text)
						self.view['card_layout'].attach(lbl, col, col+1, row+1, row+2, xpadding=3)
						lbl.show()
					
					# calculate score
					if cards[card_index] != -1:
						score += CARDVALUE[cards[card_index]]
						
						# Test for idiot's array
						if CARDVALUE[cards[card_index]] == 0:
							idiot_cards[0] = True
						elif CARDVALUE[cards[card_index]] == 2:
							idiot_cards[1] = True
						elif CARDVALUE[cards[card_index]] == 3:
							idiot_cards[2] = True
					else:
						score_unknown = True
					
					card_index += 1
				
				except IndexError: # occurs when odd number of cards
					pass
		
		# resize window to minimum possible
		if self.view['player_window'].get_property('visible'):
			min_width, min_height = self.view['player_window'].size_request()
			self.view['player_window'].resize(min_width, min_height)
		
		# Score type
		score_type = None
		
		if idiot_cards == [True, True, True] and len(cards) == 3:
			score_type = "Idiot's Array"
		elif score in (23, -23):
			score_type = "Pure Sabacc"
		elif score == 0 or score > 23 or score < -23:
			score_type = "Bomb out"
			
		if score_unknown:
			self.view['score_label'].set_text("Unknown")
			self.view['score_type_label'].set_text('')
		else:
			self.view['score_label'].set_text('%i' %score)
			if score_type == None:
				self.view['score_type_label'].set_text('')
			else:
				self.view['score_type_label'].set_text(' (%s)' %score_type)
	
	def update_labels(self, credit_mod=0):
		'''Updates status and credits information labels with correct
		values. If credit_mod is set, credit value will be modified by the
		value of credit_mod.'''
		
		if self.model.status == self.model.statuses['begin']:
			text = "Waiting for game to begin..."
		elif self.model.status == self.model.statuses['in_game']:
			text = "In game"
		elif self.model.status == self.model.statuses['end']:
			text = "Waiting for game to end..."
		else:
			self.model.agent.interface.write_error(
				'Error setting status for agent %s!' %self.model.name)
			return
		self.view['status_label'].set_text(text)
		
		self.model.credits = self.model.agent.credits + credit_mod
		self.adapt('credits', 'credits_label')
	
	pass # end of class PlayCtrl
