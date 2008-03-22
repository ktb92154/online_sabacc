#!/usr/bin/env python

import glob
from distutils.core import setup
from __init__ import __version__, __license__

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
    download_url = 'http://sourceforge.net/project/showfiles.php?group_id=209559',
    package_dir = {'sabacc': ''},
    packages = ['sabacc', 'sabacc.back', 'sabacc.front'],
    scripts = ['bin/sabacc'],
    data_files = [('share/applications', ['bin/sabacc.desktop']),
                  ('share/doc/sabacc', ['AUTHORS', 'COPYING', 'INSTALL', 'NEWS', 'README']),
                  ('share/man/man6', ['man/sabacc.6']),
                  ('share/sabacc/glade', ['glade/sabacc.glade']),
                  ('share/sabacc/cardsets/swag', glob.glob('cardsets/swag/*.png')),
                  ('share/sabacc/agents', glob.glob('agents/*.xml')),
                  ('share/sabacc/templates', ['templates/agent.xml']),
                  ('share/pixmaps', ['pixmaps/sabacc.png']) ],
        # Py2exe below this line
        windows = [{'script' : 'bin/sabacc',
                'icon_resources': [(1, 'pixmaps/sabacc.ico')] }],
        options = {'py2exe': {'packages' : 'encodings',
                'includes' : 'cairo, pango, pangocairo, atk, gobject, gtk.glade, _xmlplus, _xmlplus.sax.drivers2.drv_pyexpat' } },
)

