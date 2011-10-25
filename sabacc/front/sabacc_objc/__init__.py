#
#  __init__.py
#  Sabacc
#
#  Created by Joel Cross on 08/02/2010.
#  Copyright (c) 2010 __MyCompanyName__. All rights reserved.
#

__all__ = "ctrls models views common interface".split()

import sys

def setup_path():
	"""Sets up the python include paths to include needed directories"""
	from sabacc.constants import base_dir, share_dir
	import os.path

	if os.path.exists(share_dir):
		interface_dir = os.path.join(base_dir, 'lib', 'python%i.%i' %sys.version_info[:2], 'site-packages', 'sabacc', 'front', 'guiInterface')
	else:
		interface_dir = os.path.join(base_dir, 'sabacc', 'front', 'guiInterface')

	sys.path.insert(0, interface_dir)

def start_app():
	'''Starts up the GUI using the MVC method'''
	setup_path()
	'''
    from models.game_model import GameModel
	from ctrls.game_ctrl import GameCtrl
	from views.game_view import GameView

	gtk.gdk.threads_init()
	model = GameModel()
	ctrl = GameCtrl(model)
	view = GameView(ctrl)

	try:
		gtk.gdk.threads_enter()
		gtk.main()
		gtk.gdk.threads_leave()
	except KeyboardInterrupt:
		sys.exit(1)
    '''
	#import modules required by application
	import objc
	import Foundation
	import AppKit

	from PyObjCTools import AppHelper

	# import modules containing classes required to start application and load MainMenu.nib
	#import SabaccAppDelegate

	# pass control to AppKit
	AppHelper.runEventLoop()
