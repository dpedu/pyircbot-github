#!/usr/bin/env python
from botlibs import ModuleBase
from botlibs import Tools
import random
import yaml
import os
class Scramble(ModuleBase.ModuleBase):
	def __init__(self, bot):
		# init hte base module
		ModuleBase.ModuleBase.__init__(self, bot);
		# the NAME of this module
		self.moduleName="Scramble"
		# Dictionary
		self.wordsCount=0;
		self.wordsFile = self.getFilePath("words.txt")
		wordsF = open(self.wordsFile, "r")
		while True:
			word = wordsF.readline()
			if word=="":
				break
			self.wordsCount+=1
		wordsF.close
		self.currentWord = None
		self.scrambled = None
		self.log("Loaded %s words" % str(self.wordsCount))
		
		# Load scores
		self.scoresFile = self.getFilePath("scores.yml")
		if not os.path.exists(self.scoresFile):
			yaml.dump({}, file(self.scoresFile, 'w'))
		self.scores = yaml.load(file(self.scoresFile, 'r'))
		
		# hook our local method "repeat" to the "PRIVMSG" hook
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.scramble)]
		# let the user know we've loaded
		print "Scramble loaded"
	def scramble(self, args, prefix, trailing):
		sender = self.bot.extract_nick_from_prefix(prefix)
		if self.currentWord and trailing.strip().lower() == self.currentWord:
			playerScore = self.getScore(sender, 1)
			self.bot.do_privmsg(args[0], "%s guessed the word - %s! %s now has %s points." % (sender, self.currentWord, sender, playerScore))
			self.currentWord = None
			return
		
		cmd = Tools.messageHasCommand(".scramble", trailing)
		if cmd:
			if self.currentWord:
				self.bot.do_privmsg(args[0], "Current word is - %s (%s letters)" % (self.scrambled, len(self.scrambled)))
			else:
				f = open(self.wordsFile, "r")
				skip = random.randint(0, self.wordsCount)
				while skip>=0:
					f.readline()
					skip-=1
				self.currentWord = f.readline().strip().lower()
				self.log("Word is: %s"%self.currentWord)
				f.close()
				
				self.scrambled = ""
				
				for subword in self.currentWord.split(" "):
					self.scrambled+=self.scrambleWord(subword)+ " "
				self.scrambled = self.scrambled.strip()
				
				self.bot.do_privmsg(args[0], "New scrambled word - %s " % (self.scrambled))
	def scrambleWord(self, word):
		scrambled = list(word)
		random.shuffle(scrambled)
		return ''.join(scrambled).lower()
	def saveScores(self):
		yaml.dump(self.scores, file(self.scoresFile, 'w'))
	def getScore(self, player, add=0):
		player = player.lower()
		if not player in self.scores:
			self.scores[player] = 0
		if not add == 0:
			self.scores[player]+=add
			self.saveScores()
		
		return self.scores[player]