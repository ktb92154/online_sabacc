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
		from common import Connect
		Connect(self.view['computer_button'], 'event', self.computer_button_event)
		Connect(self.view['game_window'], 'delete-event', self.quit_button_clicked)
		Connect(self.view['new_agent_menu'], 'activate', self.agent_menu_response, False)
		Connect(self.view['load_agent_menu'], 'activate', self.agent_menu_response, True)

	def register_adapters(self):
		# setup of adapters
		self.update_labels()
	
	# Handlers for signals:
	def human_button_clicked(self, button):
		'''Handler for 'add human' button'''
		self._create_player_window()
		
	def computer_button_event(self, button, event):
		'''Handler for 'add computer' button'''
		if event.type == gtk.gdk.BUTTON_PRESS:
			gtk.gdk.threads_enter()
			self.view['computer_button_menu'].popup(None, None, None, event.button, event.time)
			gtk.gdk.threads_leave()
	
	def agent_menu_response(self, widget, agent_exists):
		'''Handler for 'create new' and 'load existing' menu items'''
		if agent_exists:
			new_file = False
			
			# Create dialog
			message = "Please select the agent file"
			gtk.gdk.threads_enter()
			d = gtk.FileChooserDialog(title=message, parent=self.view['game_window'],
			buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
			gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
			
			from sabacc.constants import agent_dir
			
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
			d.set_current_folder(agent_dir)
			
			# Show dialog
			resp=d.run()
			filename = d.get_filename()
			d.destroy()
			gtk.gdk.threads_leave()
			if resp == gtk.RESPONSE_REJECT:
				return
		
		else: # new agent
			new_file = True
			
			# Set up dialog
			title = "Create agent"
			message = "Please enter a name and rule set for the new agent:"
			gtk.gdk.threads_enter()
			d = gtk.Dialog(title, self.view['game_window'], gtk.DIALOG_MODAL,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
				gtk.STOCK_OK, gtk.RESPONSE_OK))
			main_layout = gtk.VBox(spacing=10)
			message_label = gtk.Label(message)
			main_layout.add(message_label)
			options = gtk.Table(2, 2)
			
			# labels
			name_label = gtk.Label("Name:")
			options.attach(name_label, 0, 1, 0, 1, xpadding=10, ypadding=5)
			ruleset_label = gtk.Label("Rule set:")
			options.attach(ruleset_label, 0, 1, 1, 2, xpadding=10, ypadding=5)
			
			# name entry
			name_entry = gtk.Entry()
			name_entry.set_activates_default(True)
			options.attach(name_entry, 1, 2, 0, 1)
			
			# ruleset entry
			ruleset_layout = gtk.HBox()
			from sabacc.get_settings import rule_sets
			rulesets=rule_sets.keys()
			
			self.new_ruleset = rulesets[0]
			button = None
			
			from common import Connect
			for ruleset in rulesets:
				button = gtk.RadioButton(group=button, label=str.capitalize(ruleset))
				Connect(button, 'clicked', self.set_new_ruleset, ruleset)
				ruleset_layout.add(button)
			
			options.attach(ruleset_layout, 1, 2, 1, 2)
			main_layout.add(options)
			
			d.vbox.set_spacing(10)
			d.set_default_response(gtk.RESPONSE_OK)
			d.vbox.pack_start(main_layout, True, True, 0)
			main_layout.show_all()
			
			while True:
				resp = d.run()
				name = None
				ruleset = self.new_ruleset
				
				if resp != gtk.RESPONSE_OK:
					d.destroy()
					gtk.gdk.threads_leave()
					del(self.new_ruleset)
					return
					
				# get values from input
				name = name_entry.get_text()
				
				if name == "" or ruleset == None:
					message_label.set_text("Please fill in all fields!")
				else:
					d.destroy()
					del(self.new_ruleset)
					break
			gtk.gdk.threads_leave()
			
			# make temporary file
			from tempfile import mkstemp
			from sabacc.back import xml_tools
			
			handler, filename = mkstemp('.xml', 'sabacc_', text=True)
			from os import close
			close(handler)
			
			if not xml_tools.create_agent(filename, name, ruleset):
				Game.interface.write_error("Error creating temporary file!")
				from os import remove
				remove(filename)
				return
		
		# add player to game
		from interface import playerInterface
		player_interface = playerInterface(None, None)
		player_interface.new_file = new_file
		
		agent = Game.add_player(filename, player_interface, human=False)
		if not agent:
			# Error already displayed
			return
		
		self._create_player_window(agent.name)
	
	def set_new_ruleset(self, widget, ruleset):
		'''Sets the ruleset for the new agent'''
		self.new_ruleset = ruleset
	
	def start_button_clicked(self, button):
		'''Handler for 'start game' button'''
		
		# Set up dialog
		message = "Please enter a buy-in price:"
		gtk.gdk.threads_enter()
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
		gtk.gdk.threads_leave()
		
		if resp != gtk.RESPONSE_OK:
			return
		
		self.model.last_ante=int(text_entry.get_text())
		button.set_sensitive(False)
	
		for player in self.players:
			player.model.status = player.model.statuses['in_game']
			player.model.active = True
			if not player.model.is_human:
				gtk.gdk.threads_enter()
				for index in range(3):
					player.view['move%i_button' %(index+1)].hide()
				gtk.gdk.threads_leave()
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
		
		# Make sure no-one needs to save
		for player in self.players:
			if not player.confirm_save_game():
				break
		else:
			# Remove all temporary files
			for player in self.players:
				if player.model.agent.interface.new_file:
					from os import remove
					remove(player.model.agent.filename)
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
		
		gtk.gdk.threads_enter()
		self.adapt('num_players', 'players_label')
		self.adapt('hand_pot', 'handpot_label')
		self.adapt('sabacc_pot', 'sabaccpot_label')
		gtk.gdk.threads_leave()
		
		# show correct details for all players
		for player in self.players:
			player.update_labels()
	
	# Private methods
	def _create_player_window(self, name=None):
		'''Creates a player window for the given agent, or creates a
		human agent and a player window for it.'''
		
		if name:
			is_human = False
		else:
			is_human = True
			
			# Set up dialog
			message = "What is your name?"
			
			gtk.gdk.threads_enter()
			d = gtk.MessageDialog(self.view['game_window'], gtk.DIALOG_MODAL,
				gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, message)
			text_entry = gtk.Entry()
			d.vbox.add(text_entry)
			text_entry.set_activates_default(True)
			text_entry.show()
			d.set_default_response(gtk.RESPONSE_OK)
			resp=d.run()
			d.destroy()
			gtk.gdk.threads_leave()
			
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
		
		# open player window
		from models.player_model import PlayerModel
		from player_ctrl import PlayerCtrl
		from views.player_view import PlayerView
		
		model = PlayerModel(self, name, is_human)
		ctrl = PlayerCtrl(model)
		view = PlayerView(ctrl)
		
		gtk.gdk.threads_enter()
		view['player_window'].set_transient_for(self.view['game_window'])
		gtk.gdk.threads_leave()
		
		self.players.append(ctrl)
	
		# update number of players
		self.update_labels()
		
		# 2 players minimum!
		if self.model.num_players == 2:
			gtk.gdk.threads_enter()
			self.view['start_button'].set_sensitive(True)
			gtk.gdk.threads_leave()
	
		Game.interface.write("%s entered the game" %name)
	
	def _play_game(self):
		'''Starts the game. This should be in a separate thread
		so as to not slow down GTK.'''
		
		Game.start_game(self.model.last_ante)
		
		import gobject
		gobject.idle_add(self._end_game)
	
	def _end_game(self):
		'''This cleans up after the end of a game.'''
		for player in self.players:
			if not player.model.is_human:
				player.model.agent.save_to_xml(stats=True)
				
				gtk.gdk.threads_enter()
				for index in range(3):
					player.view['move%i_button' %(index+1)].show()
				gtk.gdk.threads_leave()
			
			player.model.status = player.model.statuses['begin']
			player.model.active = False
		
		# Game has now finished
		self.update_labels()
		
		if Game.players_in_game >= 2:
			gtk.gdk.threads_enter()
			self.view['start_button'].set_sensitive(True)
			gtk.gdk.threads_leave()
