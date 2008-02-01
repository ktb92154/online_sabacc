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
XMLRuleAgent.py (taken from version 0.6beta1)
This module contains the XMLRuleAgent class.
"""

# import base class
from XMLAgent import XMLAgent

# Expected 'type' is 1 - Rule agent
EXPECTED_TYPE=1

class XMLRuleAgent (XMLAgent):		
	"""
	This class contains specific code for accessing and
	writing to the XML files of RuleBasedAgent objects.
	"""
	def createFile(self, name):
		# Call base class
		basestatus = XMLAgent.createFile(self, name)
		
		if basestatus == 0: # if file does not exist
			# Set type to 1
			# Get 'SabaccAppXML' element
			SabAX = self.doc.getElementsByTagName("SabaccAppXML")[0]
			
			# load 'agent' element
			agent=self.doc.getElementsByTagName("agent")[0]
			
			for x in SabAX.attributes: # for each atribute of the element
				if x.nodeName == "type": # if attribute x is the 'type'
					#Set attibute to expected type
					x.nodeValue = str(EXPECTED_TYPE)
			
			# Create 'rules' element and add to tree
			rules = self.doc.createElement("rules")
			agent.appendChild(rules)
		
			# write XML to file
			if self.saveDoc() == -1: # if I/O error occurred
				# -2 indicates that an I/O error occurred
				return -2
			else: # if file wrote OK
				return 0
		else:
			return basestatus
	
	def resetFile(self, name):
		# Call base class
		newfn, basestatus = XMLAgent.resetFile(self, name)
		
		if basestatus == 0: # if file exists
			# Create new file
			if self.createFile(name) == -2: # if I/O error occurred
				# -2 indicates that an I/O error occurred
				return ["", -2]
			else: # if new file created OK
				return [newfn, 0]
		else:
			return ["", basestatus]
	
	# method to return all rules in a list
	def getRules(self):
		if self.doc == None: # If file not in memory
			# load file into memory
			loadStatus = self.loadDoc()
			if loadStatus == -1: # if file was not found
				# -1 indicates that file was not found
				return [[],-1]
			elif loadStatus == -2: # if file not parsing
				# -2 indicates that XML is not correct
				return [[],-2]
		
		# Get all 'rule' elements
		origrules = self.doc.getElementsByTagName("rule")
		newrules = []
		
		for x in origrules: # for all rules
			rule = Rule()
			for y in x.attributes: # for all attributes of rule x
				if y.nodeName == "type": # if type
					rule.type = y.nodeValue
				elif y.nodeName == "name": # if name
					rule.name = y.nodeValue
			
			for y in x.childNodes: # for all children of rule x
				if y.nodeName == "if": # if condition
					cond = Condition()
					for z in y.attributes: # for all attributes of condition y
						if z.nodeName == "function": # if function
							fn = z.nodeValue
							# bug fix re: > and < signs
							if fn == "less":
								fn = "<"
							elif fn == "more":
								fn = ">"
							cond.function = fn
						elif z.nodeName == "score": # if score
							cond.score = int(z.nodeValue)
					# add condition to rule
					rule.conditions.append(cond)
				elif y.nodeName == "action": # if action
					# get action
					action = int(y.firstChild.nodeValue)
					
					# add action to rule
					rule.actions.append(action)
			# add rule to new list of rules
			newrules.append(rule)
		
		# return new list of rules and status
		return [newrules, 0]

	# method to save given rules to the file
	def saveRules(self, rules):
		if self.doc == None: # If file not in memory
			# load file into memory
			loadStatus = self.loadDoc()
			if loadStatus == -1: # if file was not found
				# -1 indicates that file was not found
				return -1
			elif loadStatus == -2: # if file not parsing
				# -3 indicates that XML is not correct
				return -3
		
		# get all existing rules, then remove them from the tree
		oldrules = self.doc.getElementsByTagName("rule")
		
		for x in oldrules: # for each old rule
			# remove from tree
			x.parentNode.removeChild(x)
		
		# new rules on tree
		newrules = self.doc.getElementsByTagName("rules")[0]
		
		for x in rules: # for each given rule
			# create new 'rule' element with correct attributes
			newrule = self.doc.createElement("rule")
			newrule.setAttribute("name", str(x.name))
			newrule.setAttribute("type", str(x.type))
			
			for y in x.conditions: # for all conditions of rule x
				fn = str(y.function)
				
				# bug fix re: > and < signs
				if fn == ">":
					fn = "more"
				elif fn == "<":
					fn = "less"
				
				# create new 'if' element with correct attributes
				newcond = self.doc.createElement("if")
				newcond.setAttribute("function", fn)
				newcond.setAttribute("score", str(y.score))
				
				# add element to tree
				newrule.appendChild(newcond)
			
			for y in x.actions: # for all actions of rule x
				# create new 'action' element
				newaction = self.doc.createElement("action")
				
				# create new text element and add to tree
				newtext = self.doc.createTextNode(str(y))
				newaction.appendChild(newtext)
				
				# add action element to tree
				newrule.appendChild(newaction)
			
			# add rule element to tree
			newrules.appendChild(newrule)
		
		# Save XML document to file
		if self.saveDoc() == -1: # if I/O error occurres
			# -2 indicates that an I/O error has occurred
			return -2
		else: # if file saved OK
			return 0

class Rule(object):
	def __init__(self):
		self.type=None
		self.name=None
		self.conditions=[]
		self.actions=[]
		
class Condition(object):
	def __init__(self):
		self.function=None
		self.score=0
