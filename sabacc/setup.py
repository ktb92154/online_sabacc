#!/usr/bin/env python

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
                'includes' : 'win32com.shell, cairo, pango, pangocairo, atk, gobject, gtk.glade, lxml.etree' } },
)

