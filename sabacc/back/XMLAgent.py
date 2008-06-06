# XMLAgent.py from Sabacc 0.6
#! This package has been obsoleted by sabacc.back.xml_tools
#! Please use that package instead of this one!

from sabacc.back import xml_tools
import sys

class XMLAgent (object):
	def __init__(self, filename):
		self.filename=filename
		sys.stderr.write('back.XMLAgent: This class has been obsoleted! Please use sabacc.back.xml_tools instead.\n')
		
	def exists(self):
		import os.path
		return os.path.exists(self.filename)
	
	def createFile(self, name):
		if xml_tools.create_agent(self.filename, name):
			return 0
		else:
			return -1
		
	def resetFile(self, name):
		return ['', -1]
	
	def loadDoc(self):
		return -1
	
	def saveDoc(self):
		return -1
	
	def getType(self):
		# Return expected values
		version = 0.5
		type = 1
		return [version, type]
	
	def getName(self):
		return xml_tools.get_name(self.filename)
	
	def getElement(self, elem):
		if elem == 'played':
			elem = 'games'
		elif elem == 'won':
			elem = 'wins'
		elif elem == 'lost':
			elem = 'losses'
		elif elem == 'bombouts':
			elem = 'bomb_outs'
		elif elem == 'puresabacc':
			elem = 'pure_sabaccs'
		else:
			return -1
		
		stats = xml_tools.get_stats(self.filename)
		
		return stats[elem]
	
	def setElement(self, elem, value):
		sys.stderr.write('Warning: back.XMLAgent.setElement: This method does nothing! Please use sabacc.back.xml_tools instead!\n')
		return 0
