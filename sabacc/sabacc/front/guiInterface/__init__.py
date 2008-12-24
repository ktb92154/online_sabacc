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
guiInterface (rewrite of front.* from 0.6 'Ackbar')
This module contains the GTK graphical interface and application.
"""

import gtk, sys

def setup_path():
	"""Sets up the python include paths to include needed directories"""
	from sabacc.constants import base_dir
	import os.path
	
	sys.path.insert(0, os.path.join(base_dir, 'sabacc/front/guiInterface'))

def check_requirements():
	"""Checks versions and other requirements"""
	import gtkmvc
	gtkmvc.require("1.2.0")
	return

def start_app():
	'''Starts up the GUI using the MVC method'''
	setup_path()
	check_requirements()
	from models.game_model import GameModel
	from ctrls.game_ctrl import GameCtrl
	from views.game_view import GameView
	
	gtk.gdk.threads_init()
	model = GameModel()
	ctrl = GameCtrl(model)
	view = GameView(ctrl)

	try:
		gtk.main()
	except KeyboardInterrupt:
		sys.exit(1)
