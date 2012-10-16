#! /usr/bin/env python
from botlibs import ModuleBase,Tools
import time
import os
import yaml
import random
import math


class DidYouKnowApprove(ModuleBase.ModuleBase):
	""" This is the same as the DidYouKnow module. However, the \"approved:False\" field needs 
		to be changed to true by an outside force before the fact will come up in the random"""
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="DidYouKnowApprove"
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.iknew)]
		self.loadConfig()
		self.ymlPath = self.getFilePath("library.yml")
		self.lastDyk = 0
		self.lastDykAdd = 0
		# Check if our library YML file exists
		if not os.path.exists(self.ymlPath):
			yaml.dump({"library":[{"addedBy":"System", "added":int(time.time()), "text":"This is the default factoid.", "approved":True}]}, file(self.ymlPath, 'w'))
		print "DidYouKnowApprove loaded"
	def iknew(self, args, prefix, trailing):
		
		if not args[0][0]=="#":
			return
		
		fromWho = self.bot.extract_nick_from_prefix(prefix)
		for name in self.config["banlist"]:
			if fromWho == name:
				return;
		
		# !dyk add
		cmd = Tools.messageHasCommand("!dyk add", trailing, True)
		if cmd:
			if time.time() - self.lastDykAdd < self.config["addLimitSeconds"]:
				# too soon!
				return;
			self.lastDykAdd = int(time.time())
			allowed = True
			# Bad word check
			for word in self.config["badwords"]:
				if word.lower() in cmd[2].lower():
					allowed = False
			# Dupe check
			lib = yaml.load(file(self.ymlPath, 'r'))
			for fact in lib["library"]:
				if fact["text"] == cmd[2].strip():
					allowed = False
					break
			if allowed:
				self.addFactoid(fromWho, cmd[2].strip(), args[0])
			return
		
		# !dyk
		cmd = Tools.messageHasCommand("!dyk", trailing, False)
		if cmd and cmd[2]=='':
			
			if time.time() - self.lastDyk < self.config["infoLimitSeconds"]:
				remaining = self.config["infoLimitSeconds"] - (float(time.time() - self.lastDyk))
				minutes = int(math.floor(remaining/60))
				seconds = int(remaining - (minutes*60))
				self.bot.do_privmsg(fromWho, "Please wait %s minute(s) and %s second(s)." % (minutes, seconds))
				return;
			factoid = self.loadRandomFactoid()
			if not factoid:
				return
			self.bot.do_privmsg(args[0], "<Did you know?> %s" % factoid["text"])
			self.lastDyk = int(time.time())
				
			return
		
	def loadRandomFactoid(self):
		lib = yaml.load(file(self.ymlPath, 'r'))
		listApproved = []
		
		for fact in lib["library"]:
			if fact["approved"]:
				listApproved.append(fact)
		
		if len(listApproved)==0:
			return False
		randomFact = listApproved[random.randint(0, len(listApproved)-1)]
		return randomFact
	def addFactoid(self, who, text, channel):
		lib = yaml.load(file(self.ymlPath, 'r'))
		lib["library"].append({"addedBy":who, "added":int(time.time()), "text":text, "approved":False})
		self.bot.do_privmsg(channel, "Thanks for the info, %s." % who)
		yaml.dump(lib, file(self.ymlPath, 'w'))
