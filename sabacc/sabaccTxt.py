#!/usr/bin/env python
# SabaccTxt.py
# Taken from SabaccApp version 0.5 (initial release)

import sys, getopt

def main():
	optlist, args = getopt.getopt(sys.argv[1:], "hctpr:", ["learning="])
	mode = None
	errors = False
	runs = 100
	learning = True
	
	for option in optlist:
		if option[0] == "-h":
			errors = True
			break
		elif mode == None:
			if option[0] == "-c":
				mode=0
			elif option[0] == "-t":
				mode=1
			elif option[0] == "-p":
				mode=2
		elif option[0] in ["-c", "-t", "-p"]:
			errors = True
			break
		elif option[0] == "-r":
			runs = int(option[1])
		elif option[0] == "--learning" and option[1] in ["0", "1"]:
			learning = bool(int(option[1]))
		else:
			errors = True
			break
	
	if mode == None:
		errors = True
	elif mode == 0:
		create(args)
	elif mode == 1:
		train(args, runs, learning)
	elif mode == 2:
		play(args)
	
	if errors:
		print """
Usage: """+sys.argv[0]+""" [OPTIONS] [FILENAMES]
	-h			Display this usage message
	-c			Create the agents specified by [FILENAMES]
	-t			Train the specified files the number of times
				specified by the -r option
	-p			Simulate a game between the specified agents
	
	-r runs			Set the number of runs for a training match
				(default 100)
	--learning=value	Decide whether learning is true or false
				(value must be 0 or 1, default 1)

If multiple instances of '-c', '-t' or '-p' are found, the program
will report an error.
"""
		sys.exit(1)

def create(filenames):
	from back.XMLLearningAgent import XMLLearningAgent
	import os.path
	
	for filename in filenames:
		name = os.path.basename(filename)
		if name[-4:] == ".xml":
			name = name[:-4]
		xml = XMLLearningAgent(filename)
		print "Creating WinLossAgent "+name+" in '"+filename+"'..."
		status = xml.createFile(name, 0)
		if status != 0:
			sys.stderr.write("Error creating file "+filename+". XMLLearningAgent.createFile returned "+str(status)+".\n")
			sys.exit(2)
	print ""

def train(filenames, runs, learning):
	from back import Players, Game
	
	if len(filenames) < 2:
		sys.stderr.write("Please specify two or more agents!\n")
		sys.exit(1)
	
	agents=[]
	names=[]
	for filename in filenames:
		status, name=Players.addXML(filename)
		print "Player "+name+" added to the game."
		names.append(name)
		if status != 0:
			sys.stderr.write("Error with file "+filename+". Players.addXML returned "+str(status)+".\n")
			sys.exit(2)
		for agent in Players.loaded:
			if agent.name==name:
				agents.append(agent)
				break
		else:
			sys.stderr.write("Unknown error!\n")
			sys.exit(2)
	
	for name in names:
		Game.addPlayer(name, True)
	
	print "\nBeginning "+str(runs)+" runs between agents "+str(names) + " with learning="+str(learning)
	
	# copied from playGame
	players = agents
		
	logfile = open("sabaccapp.log", "a")
		
	playertext = "\t"
	for player in players:
		playertext += player.name+"\tScore\t"
	
	logfile.write(str(learning)+playertext+str(runs)+" runs\n")
	
	for i in range(runs):
		if i%500 == 0:
			print "Beginning run " +str(i)
		# play a game
		Game.startGame()
		# add losers back into game
		for agent in players:
			if agent not in Game.get_players():
				Game.addPlayer(agent.name, learning)
		
		logentry = str(i)+"\t"
		for player in players:
			for p in Game.getLog():
				if p[0] == player.name:
					logentry += str(p[1])+"\t"
					logentry += str(p[2])
					break
			if player != players[-1]:
				logentry += "\t"
		
		logfile.write(logentry+"\n")
	
	logfile.write("\n")
	logfile.close()
	print "Finishing..."
	for agent in agents:
		print "Saving "+agent.name+" to file... ",
		agent.saveToXML()
		print "done"
	print ""
	
def play(filenames):
	print "Sorry: This interface is not yet implemented!"

if __name__ == "__main__":
	main()
