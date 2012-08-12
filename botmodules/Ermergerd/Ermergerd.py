#! /usr/bin/env python

from botlibs import ModuleBase
import re

class Ermergerd(ModuleBase.ModuleBase):
	def __init__(self, bot):
		# init hte base module
		ModuleBase.ModuleBase.__init__(self, bot);
		# the NAME of this module
		self.moduleName="Ermergerd"
		# hook our local method "repeat" to the "PRIVMSG" hook
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.msgRecieved)]
		# let the user know we've loaded
		print "Ermergerd loaded"
	def msgRecieved(self, args, prefix, trailing):
		if trailing[0:4]==".erm":
			line = trailing[5:]
			self.bot.do_privmsg(args[0], self.translate(line));
	def translate(self, text):
		specific = {
			'I':'I',
			'AWESOME':'ERSUM',
			'BANANA':'BERNERNER',
			'BAYOU':'BERU',
			'FAVORITE':'FRAVRIT',
			'FAVOURITE':'FRAVRIT',
			'GOOSEBUMPS':'GERSBERMS',
			'LONG':'LERNG',
			'MY':'MAH',
			'THE':'DA',
			'THEY':'DEY',
			'WE\'RE':'WER',
			'YOU':'U',
			'YOU\'RE':'YER'
		}
		text = text.upper();
		words = text.split(" ")
		
		translated = []
		for j in words:
			if j in specific:
				translated.append(specific[j])
				continue
			origWord = j
			
			# Drop ending vowels
			if len(origWord) > 2:
				j = re.sub(r'[AEIOU]$', '', j)
				
			# Drop dupe letters
			j = re.sub(r'[^\w\s]|(.)(?=\1)', '', j, 9999, re.I)
			# Reduce adjacent vowels to one
			j = re.sub(r'[AEIOUY]{2,}', 'E', j)
			# down -> dern
			j = re.sub(r'OW', 'ER', j, 9999)
			# PANCAKES -> PERNKERKS
			j = re.sub(r'AKES', 'ERKS', j, 9999)
			# The meat and potatoes: replace vowels with ER
			j = re.sub(r'[AEIOUY]', 'ER', j, 9999)
			
			# OH -> ER
			j = re.sub(r'ERH', 'ER', j, 9999)
			
			# MY -> MAH
			j = re.sub(r'MER', 'MAH', j, 9999)
			
			# FALLING -> FERLIN
			j = re.sub(r'ERNG', 'IN', j, 9999)
			
			# POOPED -> PERPERD -> PERPED
			j = re.sub(r'ERPERD', 'ERPED', j, 9999)
			
			# MEME -> MAHM -> MERM
			j = re.sub(r'MAHM', 'MERM', j, 9999)
			
			# Keep Y as first character
			# YES -> ERS -> YERS
			if (origWord[0:1] == 'Y'):
				word = 'Y' + word;
				
			# reduce dupe letters
			j = re.sub(r'[^\w\s]|(.)(?=\1)', '', j, 9999, re.I)
			translated.append(j)
		return ' '.join(translated)