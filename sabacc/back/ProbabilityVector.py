#!/usr/bin/env python
# ProbabilityVector class version 0.1.
# Written by Joel Cross

from settings import NUM_STATES

# numerical data
from numpy import *

class ProbabilityVector (object):
	def __init__(self, state=None):
		# array of zeros
		thisarray = zeros(NUM_STATES)
		
		# state is 0 if not given
		if state == None:
			state = 0
		elif type(state) in [list, ndarray]:
			self.populateVector(state)
			return
		
		thisarray[state] = 1
		
		self.vector = thisarray
		
	def populateVector(self, values):
		# create array object if necessary
		if type(values) == ndarray:
			thisarray = values
		else:
			thisarray = array(values)
		
		# sometimes vector may be 2d
		if thisarray.shape == (1, NUM_STATES):
			thisarray = thisarray[0]
		
		# test for compatibility with vector
		if thisarray.size != NUM_STATES: # if vector is wrong size
			# -1 indicates wrong sized list
			return -1
		
		if round(sum(thisarray), 10) != 1.0: # if vector does not sum to 1
			# -2 indicates list does not sum to 1
			return -2
			
		self.vector = thisarray
		
		return 0
	
	# this method sets the values of states 0 ... 3 to the value 0 and updates other states accordingly
	def removeTerminals(self):
		mod = 0.0
		all_states = range(NUM_STATES)
		terminals = all_states[:4]
		non_terminals = all_states[4:]
		
		for state in terminals:
			mod += self.vector[state]/(NUM_STATES-4)
			self.vector[state] = 0
			
		for state in non_terminals:
			self.vector[state] += mod
