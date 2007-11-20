#!/usr/bin/env python
# XMLLearningAgent class version 0.6.
# Written by Joel Cross

# import base class
from XMLAgent import XMLAgent

# Expected 'type' is 2: Learning agent
EXPECTED_TYPE=2

# number of states
from settings import NUM_MP_STATES

class XMLLearningAgent (XMLAgent):
	def createFile(self, name, learningType):
		# Call base class
		basestatus = XMLAgent.createFile(self, name)
		
		if basestatus == 0: # if file exists
			# Set type to 2
			# Get 'SabaccAppXML' element
			SabAX = self.doc.getElementsByTagName("SabaccAppXML")[0]
			
			for x in SabAX.attributes: # for each atribute of the element
				if x.nodeName == "type": # if attribute x is the 'type'
					#Set attibute to expected type
					x.nodeValue = str(EXPECTED_TYPE)
		
			# get 'agent' element
			agent=self.doc.getElementsByTagName("agent")[0]
			
			# Set agent's learning type to given value
			agent.setAttribute("learningtype", str(learningType))
			
			# create threshold elements
			bombthreshold = self.doc.createElement("bombthreshold")
			bombthreshold.setAttribute("value", "0.5")
			probthreshold = self.doc.createElement("probthreshold")
			probthreshold.setAttribute("value", "0.5")
			
			# create 'states' element
			states = self.doc.createElement("states")
			
			# create each individual state
			for i in range(NUM_MP_STATES): # for each state number
				# Create state and set number
				x = self.doc.createElement("state")
				x.setAttribute("number", str(i))
				
				# Create 'visited' and initialise to 0
				visited = self.doc.createElement("visited")
				zero = self.doc.createTextNode(str(0))
					
				# Add text to field
				visited.appendChild(zero)
					
				# Add field to state
				x.appendChild(visited)
					
				# Create 'visited' and 'value' and initialise to 0
				for j in range(3): # states 0, 1, 2
					value = self.doc.createElement("value")
					value.setAttribute('state', str(j))
					zero = self.doc.createTextNode(str(0))
					
					# Add text to field
					value.appendChild(zero)
					
					# Add field to state
					x.appendChild(value)
				
				# Add state to state list
				states.appendChild(x)
			
			# Add threshold and state list to tree
			agent.appendChild(bombthreshold)
			agent.appendChild(probthreshold)
			agent.appendChild(states)

			# write XML to file
			if self.saveDoc() == -1: # if I/O error occurred
				# -2 indicates that an I/O error occurred
				return -2
			else: # if file wrote OK
				return 0
		else:
			return basestatus

	def resetFile(self, name, learningType):
		# Call base class
		newfn, basestatus = XMLAgent.resetFile(self, name)
		
		if basestatus == 0: # if file exists
			# Create new file
			if self.createFile(name, learningType) == -2: # if I/O error occurred
				# -2 indicates that an I/O error occurred
				return ["", -2]
			else: # if new file created OK
				return [newfn, 0]
		else:
			return ["", basestatus]
		
	def getLearningType(self):
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
		
		# Get 'learningtype' attribute
		for x in agent.attributes: # for each atribute of the element
			if x.nodeName == "learningtype": # if attribute x is the learning type
				# Return learning type
				return int(x.nodeValue)
		else: # if learning type not found
			return -1
		
	
	def getStateVisited(self):
		if self.doc == None: # If file not in memory
			# load file into memory
			loadStatus = self.loadDoc()
			if loadStatus == -1: # if file was not found
				# -2 indicates that file was not found
				return [-2, []]
			elif loadStatus == -2: # if file not parsing
				# -3 indicates that XML is not correct
				return [-3, []]
		
		# Get list of states
		states = self.doc.getElementsByTagName("state")
		statelist = []
		for num in range(NUM_MP_STATES):
			statelist.append(None)
		
		for state in states: # for each state
			i=int(state.attributes[0].nodeValue)
			for x in state.childNodes: #for all sub-nodes
				if x.nodeName == "visited":
					statelist[i] = int(x.firstChild.nodeValue)
					break
			else:
				#-3 indicates that state information is badly formatted
				return [-3, []]
		
		if None in statelist: # if state not found
			return [-1, []]
		
		return [0, statelist]
	
	def setStateVisited(self, visited):
		if self.doc == None: # If file not in memory
			# load file into memory
			loadStatus = self.loadDoc()
			if loadStatus == -1: # if file was not found
				# -1 indicates that file was not found
				return -1
			elif loadStatus == -2: # if file not parsing
				# -3 indicates that XML is not correct
				return -3
		
		# Get list of states
		states = self.doc.getElementsByTagName("state")
		
		for state in states: # for each state
			i=int(state.attributes[0].nodeValue)
			for x in state.childNodes: #for all sub-nodes
				if x.nodeName == "visited":
					x.firstChild.nodeValue = str(visited[i])
					visited[i] = None
			else:
				#-3 indicates that state information is badly formatted
				return -3
		
		for state in visited:
			if state==None: # if state not found
				return -4
		
		# write XML to file
		if self.saveDoc() == -1: # if I/O error occurred
			# -2 indicates that an I/O error occurred
			return -2
		else: # if file wrote OK
			return 0
		
	def getStateValue(self):
		if self.doc == None: # If file not in memory
			# load file into memory
			loadStatus = self.loadDoc()
			if loadStatus == -1: # if file was not found
				# -2 indicates that file was not found
				return [-2, []]
			elif loadStatus == -2: # if file not parsing
				# -3 indicates that XML is not correct
				return [-3, []]
		
		# Get list of states
		states = self.doc.getElementsByTagName("state")
		statelist = []
		for num in range(NUM_MP_STATES):
			statelist.append(None)
		
		for state in states: # for each state
			i=int(state.attributes[0].nodeValue)
			values = [None, None, None]
			for x in state.childNodes: #for all sub-nodes
				if x.nodeName == "value":
					action = int(x.attributes[0].nodeValue)
					values[action] = float(x.firstChild.nodeValue)
			if None in values:
				return [-3, []]
			statelist[i] = values
		
		if None in statelist: # if state not found
			return [-1, []]
			
		return [0, statelist]
		
	def setStateValue(self, value):
		if self.doc == None: # If file not in memory
			# load file into memory
			loadStatus = self.loadDoc()
			if loadStatus == -1: # if file was not found
				# -1 indicates that file was not found
				return -1
			elif loadStatus == -2: # if file not parsing
				# -3 indicates that XML is not correct
				return -3
		
		# Get list of states
		states = self.doc.getElementsByTagName("state")
		
		for state in states: # for each state
			i=int(state.attributes[0].nodeValue)
			done = [False, False, False]
			for x in state.childNodes: #for all sub-nodes
				if x.nodeName == "value":
					action = int(x.attributes[0].nodeValue)
					x.firstChild.nodeValue = str(value[i][action])
					done[action] = True
			if done != [True, True, True]:
				#-3 indicates that state information is badly formatted
				return -3
			value[i] = None
		
		for state in value: # if state not found
			if state != None:
				return -4
		
		# write XML to file
		if self.saveDoc() == -1: # if I/O error occurred
			# -2 indicates that an I/O error occurred
			return -2
		else: # if file wrote OK
			return 0
	
	def getThresholds(self):
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
			# Get thresholds
			bombthreshold = self.doc.getElementsByTagName("bombthreshold")[0]
			probthreshold = self.doc.getElementsByTagName("probthreshold")[0]
		except IndexError: # if element not found
			return -1
		
		bombvalue=float(bombthreshold.attributes[0].nodeValue)
		probvalue=float(probthreshold.attributes[0].nodeValue)
		
		# Return value as integer
		return [bombvalue, probvalue]
		
	def setThresholds(self, bombvalue, probvalue):
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
			# Get thresholds
			bombthreshold = self.doc.getElementsByTagName("bombthreshold")[0]
			probthreshold = self.doc.getElementsByTagName("probthreshold")[0]
		except IndexError: # if element not found
			# -3 indicates that the file is badly formatted
			return -3
		
		bombthreshold.attributes[0].nodeValue=str(bombvalue)
		probthreshold.attributes[0].nodeValue=str(probvalue)
		
		# Save XML document to file
		if self.saveDoc() == -1: # if I/O error occurres
			# -2 indicates that an I/O error has occurred
			return -2
		else: # if file saved OK
			return 0
