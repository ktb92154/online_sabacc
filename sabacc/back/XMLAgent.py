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
XMLAgent.py version 0.6beta1
This module contains the XMLAgent class.
"""

# OS File tools
import os, sys

# Date for backups
from datetime import datetime

# XML Printer and Reader
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2

# XML Parse exception
from xml.sax._exceptions import SAXParseException

# import settings
from settings import SABAX_VERSION

# Find base dir and share dir
if hasattr(sys, 'frozen'):  # If py2exe distribution.
	currentdir = os.path.dirname(sys.executable)
	basedir = os.path.abspath(currentdir)
else:
	currentdir = os.path.dirname(os.path.abspath(sys.argv[0]))
	basedir = os.path.normpath(os.path.join(currentdir, '..'))
sharedir = os.path.join(basedir, 'share')

# Template directory
templatedir = os.path.join(basedir, "templates")
if not os.path.exists(templatedir):
	templatedir = os.path.join(sharedir, "sabacc", "templates")

# Template filename
TEMPLATE_FILE = os.path.join(templatedir,"agent.xml")

class XMLAgent (object):
	"""
	This is an abstract class containing methods for
	creating, reading and writing SabaccAppXML files.
	"""
	def __init__(self, filename):
		self.filename=filename
		self.doc=None
		
	def exists(self):
		return os.path.exists(self.filename)
	
	def createFile(self, name):
		# create reader object
		reader = Sax2.Reader()
		
		# Load DOM for template file
		try:
			self.doc = reader.fromStream(TEMPLATE_FILE)
		except ValueError: # template not found
			sys.stderr.write("Error: template file "+TEMPLATE_FILE+" not found!\n")
			return -1 # template not found
		
		# Get 'SabaccAppXML' element
		SabAX = self.doc.getElementsByTagName("SabaccAppXML")[0]
		
		for x in SabAX.attributes: # for each atribute of the element
			if x.nodeName == "version": # if attribute x is the 'version'
				#Set attibute to current version
				x.nodeValue = str(SABAX_VERSION)
		
		# Get 'agent' element
		agent = self.doc.getElementsByTagName("agent")[0]
		
		# Set agent's name to given name
		for x in agent.attributes:
			if x.nodeName == "name": # if x is the name
				# Set x to correct value
				x.nodeValue=name
		
		# don't write XML to file - derived classes will do this!
		return 0
		
	def resetFile(self, name):
		if self.exists(): # if file already exists
			# Get current date
			now = datetime.today().strftime("%d-%m-%y")
			
			# Multiple backups allowed on same day
			backupfn = self.filename
			tries = 0
			extra = ""
			
			while os.path.exists(backupfn):
				if tries >= 1: # if we've tried already
					extra = "_" + str(tries)
				# New filename will be 'oldfilename.date.backup'
				# if this already exists then '_tries' will follow the date
				backupfn = self.filename + "." + now + extra + ".backup"
				tries += 1
			
			try:
				# Rename the file
				os.rename(self.filename, backupfn)
			except IOError: # if I/O error occurred
				# -2 indicates that an I/O error occurred
				return ["", -2]
			
			# Don't create new file; let inherited classes do that
			return [backupfn, 0]
			
		else: # if file does not exist
			# -1 indicates that the file does not exist
			return ["", -1]
	
	def loadDoc(self):
		reader = Sax2.Reader()
		
		try:
			# load DOM for file
			self.doc = reader.fromStream(self.filename)
			return 0
		except ValueError: # if file not found
			# -1 indicates that file was not found
			return -1
		except SAXParseException: # if file not parsing correctly
			# -2 indicates file is wrong format
			return -2
	
	def saveDoc(self):
		try:
			# Create file object for writing
			file = open(self.filename, 'w')
		except IOError: # if I/O error occurred
			# -1 indicates that an I/O error occurred
			return -1
			
		# Write XML to file, then close
		PrettyPrint(self.doc, file)
		file.close()
		
		return 0
			
	
	def getType(self):
		if self.doc == None: # If file not in memory
			# load file into memory
			loadStatus = self.loadDoc()
			if loadStatus == -1: # if file was not found
				# -2 indicates that file was not found
				return [-2, -2]
			elif loadStatus == -2: # if file not parsing
				# -1 indicates that XML is not correct
				return [-1, -1]
		
		try:
			# Get 'SabaccAppXML' element
			SabAX = self.doc.getElementsByTagName("SabaccAppXML")[0]
		except IndexError: # if element not found
			# -1 indicates that document is not correctly formatted
			return [-1, -1]
		
		# Get type and version from file
		version = None
		type = None
		
		for x in SabAX.attributes: # for each atribute of the element
			if x.nodeName == "version": # if attribute x is the version
				version = float(x.nodeValue)
			elif x.nodeName == "type": # if attribute x is the 'type'
				try:
					type = int(x.nodeValue)
				except ValueError: # if field is empty
					type = None
		
		if version == None or type == None: # if version or type are not found
			# -1 indicates that the document is not correctly formatted
			return [-1, -1]
			
		else:
			# Return version and type in a list
			return [version, type]
	
	def getName(self):
		if self.doc == None: # If file not in memory
			# load file into memory
			loadStatus = self.loadDoc()
			if loadStatus == -1: # if file was not found
				# -2 indicates that file was not found
				return -2
			elif loadStatus == -2: # if file not parsing
				# -3 indicates that XML is not correct
				return -3
		
		try:
			# Get 'agent' element
			agent = self.doc.getElementsByTagName("agent")[0]
		except IndexError: # if element not found
			return -1
		
		# Get 'name' attribute
		for x in agent.attributes: # for each atribute of the element
			if x.nodeName == "name": # if attribute x is the name
				# Return name
				return x.nodeValue
		else: # if name not found
			return -1
	
	def getElement(self, elem):
		if self.doc == None: # If file not in memory
			# load file into memory
			loadStatus = self.loadDoc()
			if loadStatus == -1: # if file was not found
				# -2 indicates that file was not found
				return -2
			elif loadStatus == -2: # if file not parsing
				# -3 indicates that XML is not correct
				return -3
		
		try:
			# Get required element
			element = self.doc.getElementsByTagName(elem)[0]
		except IndexError: # if element not found
			return -1
		
		# Return value as integer
		return int(element.firstChild.nodeValue)
	
	def setElement(self, elem, value):
		if self.doc == None: # If file not in memory
			# load file into memory
			loadStatus = self.loadDoc()
			if loadStatus == -1: # if file was not found
				# -1 indicates that file was not found
				return -1
			elif loadStatus == -2: # if file not parsing
				# -3 indicates that XML is not correct
				return -3
		
		try:
			# Get required element
			element = self.doc.getElementsByTagName(elem)[0]
		except IndexError: # if element not found
			# -3 indicates that the file is badly formatted
			return -3
		
		# Set value
		element.firstChild.nodeValue = str(value)
		
		# Save XML document to file
		if self.saveDoc() == -1: # if I/O error occurres
			# -2 indicates that an I/O error has occurred
			return -2
		else: # if file saved OK
			return 0
