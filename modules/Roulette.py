#!/usr/bin/env python
from botlibs import ModuleBase,Tools
import random

class Roulette(ModuleBase.ModuleBase):
	def __init__(self, bot):
		# init hte base module
		ModuleBase.ModuleBase.__init__(self, bot);
		# the NAME of this module
		self.moduleName="Roulette"
		# "Game" slots
		self.chambers = None;
		# hook our local method "repeat" to the "PRIVMSG" hook
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.roulette)]
		# let the user know we've loaded
		print "Roulette loaded"
	def roulette(self, args, prefix, trailing):
		cmd = Tools.messageHasCommand(".roulette", trailing)
		if cmd:
			sender = self.bot.extract_nick_from_prefix(prefix)
			if self.chambers == None:
				self.reload(args[0])
				return
			
			if self.chambers.pop(0):
				self.bot.do_kick(args[0], sender, "BANG! You died.")
				self.chambers = None
			else: 
				self.bot.do_privmsg(args[0], "Click!")
				if len(self.chambers)==1:
					self.reload(args[0])
	def reload(self, channel):
		self.chambers = [False, False, False, False, False, False]
		self.chambers[random.randint(0, 5)]=True
		self.bot.do_action(channel, "reloads 6 new bullets into the chambers.")