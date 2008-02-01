"""
GTK Front-end for Sabacc
"""

import sys
import os.path

# Find base dir and share dir
if hasattr(sys, 'frozen'):  # If py2exe distribution.
	currentdir = os.path.dirname(sys.executable)
	basedir = os.path.abspath(currentdir)
else:
	currentdir = os.path.dirname(os.path.abspath(sys.argv[0]))
	basedir = os.path.normpath(os.path.join(currentdir, '..'))
sharedir = os.path.join(basedir, 'share')

# Find Glade file
name = "sabacc.glade"

if os.path.exists(sharedir):
    gladefile = os.path.join(sharedir, 'sabacc', 'glade', name)
else:  # Root of source distribution.
    gladefile = os.path.join(basedir, 'glade', name)
