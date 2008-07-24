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
interface.py (rewrite of front.wnd{Game,Player} and front.gtkPlayerInterface from 0.6 'Ackbar')
This module contains GUI interfaces for the game and players.
"""

from sabacc.front import nullInterface

class gameInterface (nullInterface.gameInterface):
	'''
	This is a GUI-based interface for games.
	'''
	def __init__(self, controller):
		self.controller = controller
	
	def write(self, text, error=False):
		'''Writes the given text to the controller's message label.
		If 'error' is true, the message will be in red.'''
		
		from datetime import datetime
		from xml.sax.saxutils import escape
		
		message_label = self.controller.view['message_label']
		orig_text = self.controller.model.messages
		now = datetime.today().strftime("(%H:%M:%S)")
		
		if error:
			final_text = "<span color='red' weight='bold'>%s</span>\n%s" \
				%(escape(text), orig_text)
		else:
			final_text = "%s %s\n%s" %(now, escape(text), orig_text)
		
		self.controller.model.messages = final_text
		message_label.set_markup(final_text)
		
		# If a player has left, set correct status
		name = None
		if text[-13:] == "left the game":
			name = text[:-14]
		elif text[-10:] == "bombed out":
			name = text[:-11]
				
		if name == None:
			return
		
		# Set agent to 'end game' if they are
		for player in self.controller.players:
			if player.model.name == name:
				player.model.status = player.model.statuses['end']
				player.model.active = False
				player.update_labels()
				break
	
	def write_error(self, text):
		'''Writes the given error to both the stderr and the GUI'''
		nullInterface.gameInterface.write_error(self, text)
		self.write(text, error=True)
		
	def show_cards(self, cards, name=None, show_all=True):
		'''Finds the named player and shows his cards'''
		
		if name==None:
			# Show whose cards??
			return
		
		# find player by name
		for player in self.controller.players:
			if player.model.name == name:
				player.model.agent.interface.show_cards(cards, show_all)
				break
		else:
			self.write_error('Error: Player %s not found!' %name)
		
class playerInterface (nullInterface.playerInterface):
	'''
	This is a GUI-based interface for individual players.
	'''
	def __init__(self, name, controller):
		self.name = name
		self.controller = controller
		self.signals = [None, None, None] # Signals connected to buttons
		self.wait = False
		self.new_file = False # is this a new, temporary file?
		
	def show_cards(self, cards, name=None, show_all=False):
		'''Calls the GUI to show the cards to the user.'''
		self.controller.model.cards = cards
		self.controller.update_cards(show_all)
		
	def get_move(self, cards):
		'''Calls the GUI to prompt the user for a move.'''
		import gobject
		self.wait = True
		
		# Prompt for new move if necessary
		gobject.idle_add(self._prompt_for_new_turn)
		while self.wait:
			pass
		
		self.wait = True
		gobject.idle_add(self._ask_for_move)
		while self.wait:
			pass
		
		chosen_move = self.chosen_move
		del(self.chosen_move)
		return chosen_move
	
	def get_bet(self, cards, must_match):
		'''Calls the GUI to prompt the user for a bet.'''
		
		import gobject
		self.wait = True
		# Prompt for new move if necessary
		gobject.idle_add(self._prompt_for_new_turn)
		while self.wait:
			pass
		
		self.wait = True
		gobject.idle_add(self._ask_for_bet, must_match)
		while self.wait:
			pass
		
		chosen_move = self.chosen_move
		del(self.chosen_move)
		return chosen_move
		
	def game_status(self, won, cards, credits=None):
		'''Calls the GUI to report the status of the game to the user.'''
		
		import gobject
		self.wait = True
		gobject.idle_add(self._show_game_status, won)
		while self.wait:
			pass
	
	# Private methods
	def _ask_for_move(self):
		'''Prompts the user for the next move to take.'''
		
		# Update all labels
		self.controller.model.game_controller.update_labels()
		
		from sabacc.back.Game import callable
		from sabacc.back.settings import moves
		
		self.controller.view['betspinner'].hide()
		
		# 'Draw 'button
		self.controller.view['move1_button'].set_label("Draw a card")
		self.controller.view['move1_button'].set_sensitive(True)
		self.signals[0] = self.controller.view['move1_button'].connect("clicked", self._make_move, moves['draw'])
		
		# 'Stick' button
		self.controller.view['move2_button'].set_label("Stick")
		self.controller.view['move2_button'].set_sensitive(True)
		self.signals[1] = self.controller.view['move2_button'].connect("clicked", self._make_move, moves['stick'])
		
		if callable:
			# 'Call' button
			self.controller.view['move3_button'].set_sensitive(True)
			self.signals[2] = self.controller.view['move3_button'].connect("clicked", self._make_move, moves['move_call'])
		else:
			self.signals[2] = None
	
	def _ask_for_bet(self, must_match):
		'''Prompts the user for the next bet to make.'''
		
		# Update all labels
		self.controller.model.game_controller.update_labels()
		
		from sabacc.back.Game import callable
		from sabacc.back.settings import moves
		
		# Spinner
		self.controller.view['betspinner'].set_sensitive(True)
		adj = self.controller.view['betspinner'].get_adjustment()
		adj.set_all(must_match, must_match, self.controller.model.agent.credits, 1, 1, 1)
		
		self.controller.view['betspinner'].connect("value-changed", self._update_bet_text)
		self.controller.view['betspinner'].show()
		
		# 'Bet' button
		self._update_bet_text(self.controller.view['betspinner'])
		self.signals[0] = self.controller.view['move1_button'].connect("clicked", self._make_bet)
		self.controller.view['move1_button'].set_sensitive(True)
		
		# 'Leave game' button
		self.controller.view['move2_button'].set_label("Leave game")
		self.signals[1] = self.controller.view['move2_button'].connect("clicked", self._make_move, moves['fold'])
		self.controller.view['move2_button'].set_sensitive(True)
		
		# 'Call' button
		if callable:
			self.controller.view['move3_button'].set_sensitive(True)
			self.signals[2] = self.controller.view['move3_button'].connect("clicked", self._make_move, moves['bet_call'])
	
	def _update_bet_text(self, spinner):
		'''Changes the label of the 'bet' button so as to prevent
		confusion over how to end betting.'''
		
		if int(spinner.get_value()) > 0:
			bet_text = "Bet"
		else:
			bet_text = "End betting"
			
		self.controller.view['move1_button'].set_label(bet_text)
	
	def _make_move(self, button, chosen_move):
		'''Reset the GUI after a move or bet was chosen.'''
		game_controller = self.controller.model.game_controller
		
		# Protect from other humans
		if game_controller.model.humans_in_game >= 2:
			self.controller.model.this_human_in_play = False
			self.controller.update_cards()
			
		self.chosen_move = chosen_move
		
		for counter in range(3): # [0, 1, 2]
			if self.signals[counter] != None:
				self.controller.view['move%i_button' %(counter+1)].disconnect(self.signals[counter])
				self.controller.view['move%i_button' %(counter+1)].set_sensitive(False)
				self.signals[counter] = None
		
		self.controller.view['betspinner'].set_sensitive(False)
		
		self.wait = False
		
	def _make_bet(self, button):
		'''DIscovers the correct bet amount, then makes the bet.'''
		bet = int(self.controller.view['betspinner'].get_value())
		self.controller.update_labels(credit_mod=-bet)
		self._make_move(button, bet)
	
	def _show_game_status(self, won):
		'''Report the status of the game and any winnings to the user.'''
		import gtk
		
		self.controller.update_labels()
		
		title = "Message for %s" %self.name
		if won:
			text = "Congratulations. You have won!"
		else:
			text = "Sorry. You didn't win this time."
			
		dialog = gtk.Dialog(title, self.controller.view['player_window'], gtk.DIALOG_MODAL,
			(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		dialog.connect("response", self._dialog_destroy)
		hbox = gtk.HBox()
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DIALOG)
		label = gtk.Label(text)
		hbox.add(icon)
		hbox.add(label)
		dialog.vbox.pack_start(hbox, True, True, 0)
		dialog.show_all()
		
	def _dialog_destroy(self, dialog, response):
		'''Destroy any waiting dialogs and tell any waiting
		processes to stop waiting.'''
		dialog.destroy()
		self.wait = False
		self.controller.update_cards()
		
	def _prompt_for_new_turn(self):
		'''If there's more than one human, pause between each
		move and prompt for a new turn.'''
		
		# Don't bother if there's only one human
		if self.controller.model.game_controller.model.humans_in_game < 2:
			self.wait = False
			return
		
		import gtk
		title = "New Turn"
		text = "%s's turn..." %self.name
		
		dialog = gtk.Dialog(title, self.controller.view['player_window'], gtk.DIALOG_MODAL,
			(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		dialog.connect("response", self._dialog_destroy)
		hbox = gtk.HBox()
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DIALOG)
		label = gtk.Label(text)
		hbox.add(icon)
		hbox.add(label)
		dialog.vbox.pack_start(hbox, True, True, 0)
		dialog.show_all()
		
		self.controller.model.this_human_in_play = True
