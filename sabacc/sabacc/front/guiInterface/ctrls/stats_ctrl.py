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
stats_ctrl.py (taken from Sabacc version 1.0-beta1)
This module contains the controller for the individual 'agent data' windows.
"""

from gtkmvc import Controller
from gtkmvc import adapters
import gtk
import gettext; _=gettext.gettext # gettext for translations

class StatsCtrl (Controller):
	'''
	This class contains the controller for the stats window.
	'''
	def __init__(self, model):
		Controller.__init__(self, model)
		self.new_ruleset = model.agent.ruleset
		return

	def register_view(self, view):
		'''Sets up the view and handles widget signals.'''
		Controller.register_view(self, view)
	
	def register_adapters(self):
		'''Updates all labels and inputs with correct values.'''
		
		agent = self.model.agent
		if agent.interface.new_file:
			filename = _('N/A')
		else:
			filename = agent.filename
		
		gtk.gdk.threads_enter()
		self.view['name_entry'].set_text(agent.name)
		self.view['filename_label'].set_text(filename)
		self.view['games_played_label'].set_text("%i" %agent.stats['games'])
		self.view['games_won_label'].set_text("%i" %agent.stats['wins'])
		self.view['games_lost_label'].set_text("%i" %agent.stats['losses'])
		self.view['bomb_outs_label'].set_text("%i" %agent.stats['bomb_outs'])
		self.view['pure_sabaccs_label'].set_text("%i" %agent.stats['pure_sabaccs'])
		gtk.gdk.threads_leave()
		
		from sabacc.get_settings import rule_sets
		button = None
		self.new_ruleset = agent.ruleset
		
		from common import Connect
		for ruleset in rule_sets.keys():
			gtk.gdk.threads_enter()
			button = gtk.RadioButton(group=button, label=str.capitalize(ruleset))
			if agent.ruleset == ruleset:
				button.set_active(True)
			Connect(button, 'clicked', self.set_new_ruleset, ruleset)
			button.show()
			self.view['ruleset_layout'].add(button)
			gtk.gdk.threads_leave()
	
	# Handlers for signals:
	def ok_button_clicked(self, button):
		'''Close the window and save changes.'''
		
		if self.model.agent.name != self.view['name_entry'].get_text():
			old_name = self.model.agent.name
			new_name = self.view['name_entry'].get_text()
			
			# Change name in game
			from sabacc.back import Game
			name_conflict = False
			index_to_change = None
			
			for index in range(len(Game.names)):
				if Game.names[index] == old_name:
					index_to_change = index
				elif Game.names[index] == new_name:
					name_conflict = True
					
			if name_conflict:
				Game.interface.write_error(
					_('There is already a player with the name %s. The name has not been changed.') %new_name)
			else:
				Game.names[index_to_change] = new_name
				self.model.agent.name = new_name
				self.model.player_controller.view['player_window'].set_title(new_name)
				self.model.player_controller.model.name = new_name
			
		self.model.agent.ruleset = self.new_ruleset
		self.model.player_controller.changes_occurred()
		gtk.gdk.threads_enter()
		self.view['stats_window'].destroy()
		gtk.gdk.threads_leave()
		
	def cancel_button_clicked(self, button):
		'''Close the window without saving changes.'''
		gtk.gdk.threads_enter()
		self.view['stats_window'].destroy()
		gtk.gdk.threads_leave()
	
	def name_entry_changed(self, entry):
		'''Tells the controller that the name has changed'''
		gtk.gdk.threads_enter()
		if entry.get_text() == self.model.agent.name and \
		self.new_ruleset == self.model.agent.ruleset:
			self.view['ok_button'].set_sensitive(False)
		else:
			self.view['ok_button'].set_sensitive(True)
		gtk.gdk.threads_leave()
	
	def set_new_ruleset(self, widget, ruleset):
		'''Tells the controller that the ruleset has changed'''
		if not widget.get_active():
			return
		
		gtk.gdk.threads_enter()
		if self.view['name_entry'].get_text() == self.model.agent.name and \
		ruleset == self.model.agent.ruleset:
			self.view['ok_button'].set_sensitive(False)
		else:
			self.view['ok_button'].set_sensitive(True)
		gtk.gdk.threads_leave()
		
		self.new_ruleset = ruleset
	
	# Private methods
