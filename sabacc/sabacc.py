#!/usr/bin/env python
# sabacc.py
# Taken from SabaccApp version 0.5 (initial release)
# This is the application caller, that imports all packages
# and loads the initial window.

from front import wndApp
import sys

try:
	import gtk
except:
	sys.exit(1)
	
def main():
	wndApp.window.show()
	gtk.gdk.threads_init()
	gtk.gdk.threads_enter()
	try:
		gtk.main()
	except KeyboardInterrupt:
		sys.exit(1)
	gtk.gdk.threads_leave()
	sys.exit()
	
if __name__ == "__main__":
	main()
