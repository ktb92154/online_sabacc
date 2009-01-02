#!/usr/bin/env python

try:
	# if this doesn't work, try import modulefinder
	import py2exe.mf as modulefinder
	import win32com
except ImportError:
	# no build path setup, no worries.
	pass
else:
	# Set up correct environment for Py2exe
	import sys
	for p in win32com.__path__[1:]:
		modulefinder.AddPackagePath("win32com", p)
	extra = "win32com.shell"
	__import__(extra)
	m = sys.modules[extra]
	for p in m.__path__[1:]:
		modulefinder.AddPackagePath(extra, p)
	
	# Find missing Sabacc packages
	import os.path
	base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
	interface_dir = os.path.join(base_dir, 'sabacc', 'front', 'guiInterface')
	sys.path.insert(0, interface_dir)

import glob
from distutils.core import setup
from sabacc import __version__, __license__

try:
	import py2exe
except ImportError:
	pass

setup(
	name = 'sabacc',
	version = __version__,
	license = __license__,
	author = 'Joel Cross',
	author_email = 'joel@kazbak.co.uk',
	url = 'http://sabacc.sourceforce.net/',
	description = 'An interesting card game similar to Blackjack.',
	download_url = 'http://sabacc.sourceforge.net/download',
	packages = ['sabacc', 'sabacc.back', 'sabacc.front', 'sabacc.front.guiInterface', \
	'sabacc.front.guiInterface.models', 'sabacc.front.guiInterface.views', 'sabacc.front.guiInterface.ctrls'],
	scripts = ['bin/sabacc'],
	data_files = [('share/applications', ['bin/sabacc.desktop']),
		('share/doc/sabacc', ['AUTHORS', 'COPYING', 'INSTALL', 'NEWS', 'README']),
		('share/man/man6', ['man/sabacc.6']),
		('share/sabacc/glade', ['glade/sabacc.glade']),
		('share/sabacc/cardsets/swag', glob.glob('cardsets/swag/*.png')),
		('share/sabacc/agents', ['agents/Example.xml']),
		('share/sabacc', ['settings.xml']),
		('share/pixmaps', ['pixmaps/sabacc.png', 'pixmaps/sabacc.ico']) ],
	# Py2exe below this line
	windows = [{'script' : 'bin/sabacc',
		'icon_resources': [(1, 'pixmaps/sabacc.ico')] }],
	options = {'py2exe': {'packages' : 'encodings',
		'includes' : 'win32com, cairo, pango, pangocairo, atk, gobject, gtk.glade, lxml, lxml._elementpath, inspect' } },
)

