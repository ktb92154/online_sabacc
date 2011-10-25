# Sabacc -- an interesting card game similar to Blackjack.
# Copyright (C) 2007-2008 Joel Cross.
# (The ThreadSafeView class is modified from gtkmvc.View.
# Copyright 2005-7 Roberto Cavada and Guillaume Libersat.)
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
common.py (taken from Sabacc version 1.0-beta1)
This module contains common methods for the entire GTK GUI
"""

from gtk import gdk

def _wrap(handler):
	'''Creates a wrapper for object connections.'''
	
	# Thanks to the guys at pardon-sleeuwaegen.be for this code!
	def wrapper(obj, *args):
		gdk.threads_leave()
		handler(obj, *args)
		gdk.threads_enter()
	
	return wrapper

def Connect(obj, signal, handler, *args):
	'''A thread-friendly replacement for Object.connect()'''
	
	# Thanks to the guys at pardon-sleeuwaegen.be for this code!
	return obj.connect(signal, _wrap(handler), *args)

def AutoConnect(xml, dic):
	'''A thread-friendly replacement for XMLObject.signal_autoconnect()'''
	for key in dic.keys():
		xml.signal_connect(key, _wrap(dic[key]))

from gtkmvc import View as _View
class ThreadSafeView(_View):
	'''
	We have rewritten one method of the gtkmvc View method so
	that it uses our thread-safe 'AutoConnect' method instead of
	the built-in un-thread-safe one.
	'''
	
	def _View__autoconnect_signals(self, controller):
		'''This method copyright Roberto Cavada and Guillaume Libersat'''
		
		dic = {}
		for name in dir(controller):
			method = getattr(controller, name)
			if (not callable(method)): continue
			assert(not dic.has_key(name)) # not already connected!
			dic[name] = method
			pass

		for xml in self.xmlWidgets:
			# Here is the modified line
			AutoConnect(xml, dic)
		return
