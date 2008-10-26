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
stats_ctrl.py (partial rewrite of front.wndTrain from 0.6 'Ackbar')
This module contains the controller for the individual 'agent data' windows.
"""

from gtkmvc import Controller
from gtkmvc import adapters
import gtk

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
		
		return
	
	def register_adapters(self):
		'''Updates all labels and inputs with correct values.'''
		
		agent = self.model.agent
		if agent.interface.new_file:
			filename = 'N/A'
		else:
			filename = agent.filename
		self.view['name_entry'].set_text(agent.name)
		self.view['filename_label'].set_text(filename)
		self.view['games_played_label'].set_text("%i" %agent.stats['games'])
		self.view['games_won_label'].set_text("%i" %agent.stats['wins'])
		self.view['games_lost_label'].set_text("%i" %agent.stats['losses'])
		self.view['bomb_outs_label'].set_text("%i" %agent.stats['bomb_outs'])
		self.view['pure_sabaccs_label'].set_text("%i" %agent.stats['pure_sabaccs'])
		
		from sabacc.constants import rule_sets
		button = None
		self.new_ruleset = agent.ruleset
		
		for ruleset in rule_sets.keys():
			button = gtk.RadioButton(group=button, label=str.capitalize(ruleset))
			if agent.ruleset == ruleset:
				button.set_active(True)
			button.connect('clicked', self.set_new_ruleset, ruleset)
			button.show()
			self.view['ruleset_layout'].add(button)
		
		return
	
	# Handlers for signals:
	def ok_button_clicked(self, button):
		'''Close the window and save changes.'''
		
		self.model.agent.name = self.view['name_entry'].get_text()
		self.model.agent.ruleset = self.new_ruleset
		self.model.player_controller.changes_occurred()
		self.view['stats_window'].destroy()
		
	def cancel_button_clicked(self, button):
		'''Close the window without saving changes.'''
		self.view['stats_window'].destroy()
	
	def name_entry_changed(self, entry):
		'''Tells the controller that the name has changed'''
		if entry.get_text() == self.model.agent.name and \
		self.new_ruleset == self.model.agent.ruleset:
			self.view['ok_button'].set_sensitive(False)
		else:
			self.view['ok_button'].set_sensitive(True)
	
	def set_new_ruleset(self, widget, ruleset):
		'''Tells the controller that the ruleset has changed'''
		if not widget.get_active():
			return
		
		if self.view['name_entry'].get_text() == self.model.agent.name and \
		ruleset == self.model.agent.ruleset:
			self.view['ok_button'].set_sensitive(False)
		else:
			self.view['ok_button'].set_sensitive(True)
		
		self.new_ruleset = ruleset
	
	# Private methods
	
	pass # end of class StatsCtrl
