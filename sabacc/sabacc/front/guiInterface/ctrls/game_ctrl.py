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
game_ctrl.py (rewrite of front.wnd{App,Game} from 0.6 'Ackbar')
This module contains the controller for the main game window.
"""

from gtkmvc import Controller
from gtkmvc import adapters
import gtk
from sabacc.back import Game

class GameCtrl (Controller):
	'''
	This class contains the controller for the main game window,
	where any number of agents can be loaded up to play a game.
	'''
	def __init__(self, model):
		Controller.__init__(self, model)
		
		from interface import gameInterface
		Game.interface = gameInterface(controller=self)
		
		# Variables
		self.players = [] # list of controllers for player windows

	def register_view(self, view):
		'''Sets up the view and handles widget signals.'''
		Controller.register_view(self, view)

		# setup of widgets
		self.view['game_window'].connect('delete-event', self.quit_button_clicked)

	def register_adapters(self):
		# setup of adapters
		self.update_labels()
	
	# Handlers for signals:
	def human_button_clicked(self, button):
		'''Handler for 'add human' button'''
		self._add_player(is_human=True)
		
	def computer_button_clicked(self, button):
		'''Handler for 'add computer' button'''
		self._add_player(is_human=False)
		
	def start_button_clicked(self, button):
		'''Handler for 'start game' button'''
		
		# Set up dialog
		message = "Please enter a buy-in price:"
		d = gtk.MessageDialog(self.view['game_window'], gtk.DIALOG_MODAL,
		gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, message)
		adj=gtk.Adjustment(value=self.model.last_ante, lower=0, 
			upper=500, step_incr=1)
		text_entry = gtk.SpinButton(adj)
		text_entry.set_activates_default(True)
		d.vbox.add(text_entry)
		text_entry.show()
		d.set_default_response(gtk.RESPONSE_OK)
		resp=d.run()
		d.destroy()
		
		if resp != gtk.RESPONSE_OK:
			return
		
		self.model.last_ante=int(text_entry.get_text())
		button.set_sensitive(False)
	
		for player in self.players:
			player.model.status = player.model.statuses['in_game']
			player.model.active = True
			player.update_labels()
	
		from threading import Thread
		
		# Start the game
		t = Thread(target=self._play_game, name="play_game")
		t.setDaemon(True) # this thread will exit when app exits
		t.start()
		
	def quit_button_clicked(self, button_or_window, signal=None):
		'''Handler for 'quit' button'''
		
		if Game.shift_timer != None:
			Game.shift_timer.cancel()
		gtk.main_quit()
	
	def remove_player(self, name, active=False):
		'''This is called after a player has closed their window. It
		handles cleaning up after the errant player.'''
		
		if active:
			# The player is about to be removed, so don't remove
			# him again!
			game_status = False
		else:
			game_status = Game.remove_player(name)
		
		for player in self.players:
			if player.model.name == name:
				self.players.remove(player)
				self.update_labels()
				break
		else:
			Game.interface.write_error('Error: Player %s not correctly removed!' %name)
			return False
		
		# 2 players minimum!
		if self.model.num_players < 2:
			self.view['start_button'].set_sensitive(False)
		
		if player.model.is_human:
			self.model.humans_in_game -= 1
		
		if game_status:
			# print to status bar
			Game.interface.write("%s left the game" %name)
		return True
	
	def update_labels(self):
		'''Updates player and pot information labels with correct values.'''
		
		self.model.num_players = Game.players_in_game
		self.model.hand_pot = Game.hand_pot
		self.model.sabacc_pot = Game.sabacc_pot
		
		self.adapt('num_players', 'players_label')
		self.adapt('hand_pot', 'handpot_label')
		self.adapt('sabacc_pot', 'sabaccpot_label')
		
		# show correct details for all players
		for player in self.players:
			player.update_labels()
	
	# Private methods
	def _add_player(self, is_human):
		'''Uses dialog boxes to determine player details, then
		adds to the game.'''
		if is_human:
			# Set up dialog
			message = "What is your name?"
			d = gtk.MessageDialog(self.view['game_window'], gtk.DIALOG_MODAL,
			gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, message)
			text_entry = gtk.Entry()
			d.vbox.add(text_entry)
			text_entry.set_activates_default(True)
			text_entry.show()
			d.set_default_response(gtk.RESPONSE_OK)
			resp=d.run()
			d.destroy()
			
			if resp != gtk.RESPONSE_OK:
				return
			
			name=text_entry.get_text()
			if name == "":
				return
			
			# add player to game
			from interface import playerInterface
			if Game.add_player(name, player_interface=playerInterface(name, None), human=True):
				self.model.humans_in_game += 1
			else:
				# Error already displayed
				return
		
		else:
			# Create dialog
			message = "Please select the agent file"
			d = gtk.FileChooserDialog(title=message, parent=self.view['game_window'],
			buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
			gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
			
			from front import basedir, sharedir#!
			import os.path
			agentdir = os.path.join(basedir, "agents")
			if not os.path.exists(agentdir):
				agentdir = os.path.join(sharedir, "sabacc", "agents")
			
			# Create filters
			xmlfilter = gtk.FileFilter()
			xmlfilter.add_pattern("*.xml")
			xmlfilter.set_name("XML Files")
			anyfilter = gtk.FileFilter()
			anyfilter.add_pattern("*")
			anyfilter.set_name("All Files")
			d.add_filter(xmlfilter)
			d.set_filter(xmlfilter)
			d.add_filter(anyfilter)
			d.set_current_folder(os.path.abspath(agentdir))
			
			# Show dialog
			resp=d.run()
			filename = d.get_filename()
			d.destroy()
			if resp == gtk.RESPONSE_REJECT:
				return
			
			from threading import Thread
			t = Thread(target=self._load_agent, args=[filename], name="load_agent")
			t.setDaemon(True)
			t.start()
			
			title = "Loading..."
			text = "Please wait. Loading data..."
			dialog = gtk.Dialog(title, self.view['game_window'], gtk.DIALOG_MODAL,
					(gtk.STOCK_CANCEL, gtk.RESPONSE_DELETE_EVENT))
			label = gtk.Label(text)
			dialog.vbox.pack_start(label, True, True, 0)
			dialog.show_all()
			self.view['loading'] = dialog
			resp = dialog.run()
			
			if resp == gtk.RESPONSE_DELETE_EVENT: # 'cancel' clicked
				dialog.destroy()
				return
			else:
				try:
					name = self.loaded_name
				except AttributeError: # Player already exists
					return
				
		
		# open player window
		from models.player_model import PlayerModel
		from player_ctrl import PlayerCtrl
		from views.player_view import PlayerView
		
		model = PlayerModel(self, name, is_human)
		ctrl = PlayerCtrl(model)
		view = PlayerView(ctrl)
		
		view['player_window'].set_transient_for(self.view['game_window'])
		self.players.append(ctrl)
	
		# update number of players
		self.update_labels()
		
		# 2 players minimum!
		if self.model.num_players == 2:
			self.view['start_button'].set_sensitive(True)
	
		Game.interface.write("%s entered the game" %name)
	
	def _load_agent(self, filename):
		'''Loads a computer agent in the background, so as not to
		slow down GTK.'''
		
		import gobject
		from interface import playerInterface
		agent = Game.add_player(filename, player_interface=playerInterface(None, None), human=False)
		if not agent:
			# Error already displayed
			gobject.idle_add(self.view['loading'].destroy)
			return
		
		self.loaded_name = agent.name
		agent.interface.name = agent.name
		try:
			# Workaround for GUI threading problem on Windows
			gobject.idle_add(self.view['loading'].destroy)
		except AttributeError: # loading window already gone
			pass
		
		# Wait until attributes are no longer needed, then clean up
		# and terminate thread
		from time import sleep
		sleep(1)
		try:
			del(self.loaded_name)
			self.view['loading'] = None
		except:
			pass
	
	def _play_game(self):
		'''Starts the game and cleans up afterwards. This should be in
		a separate thread so as to not slow down GTK.'''
		
		Game.start_game(self.model.last_ante)
		
		for player in self.players:
			if not player.model.is_human:
				player.model.agent.save_to_xml(stats=True)
			
			player.model.status = player.model.statuses['begin']
			player.model.active = False
		
		# Game has now finished
		self.update_labels()
		
		if Game.players_in_game >= 2:
			self.view['start_button'].set_sensitive(True)
	
	pass # end of class GameCtrl
