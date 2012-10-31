#!/usr/bin/env python
from botlibs import ModuleBase,SimpleConfigReader
import time
import os
import yaml
import random

class DidYouKnow(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="DidYouKnow"
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.iknew)]
		self.loadConfig()
		self.ymlPath = self.getFilePath("library.yml")
		self.lastDyk = 0
		self.lastDykAdd = 0
		# Check if our library YML file exists
		if not os.path.exists(self.ymlPath):
			yaml.dump({"library":[{"addedBy":"System", "added":int(time.time()), "text":"This is the default factoid."}]}, file(self.ymlPath, 'w'))
		print "DidYouKnow loaded"
	def iknew(self, args, prefix, trailing):
		lib = yaml.load(file(self.ymlPath, 'r'))
		fromWho = self.bot.extract_nick_from_prefix(prefix)
		for name in self.config["banlist"]:
			if fromWho == name:
				return;
		if trailing.startswith(".dyk"):
			afterDyk = trailing[4:].strip()
			if afterDyk == '':
				if time.time() - self.lastDyk < self.config["infoLimitSeconds"]:
					# too soon!
					return;
				self.bot.do_privmsg(args[0], "<Did you know?> %s" % self.loadRandomFactoid()["text"])
				self.lastDyk = int(time.time())
			else:
				if time.time() - self.lastDykAdd < self.config["addLimitSeconds"]:
					# too soon!
					return;
				self.lastDykAdd = int(time.time())
				allowed = True
				for word in self.config["badwords"]:
					if word in afterDyk:
						allowed = False
				if allowed:
					self.addFactoid(fromWho, afterDyk, args[0])
				else:
					self.bot.do_privmsg(args[0], "%s, that's rude!" % fromWho)
	def loadRandomFactoid(self):
		lib = yaml.load(file(self.ymlPath, 'r'))
		randomFact = lib["library"][random.randint(0, len(lib["library"])-1)]
		return randomFact
	def addFactoid(self, who, text, channel):
		lib = yaml.load(file(self.ymlPath, 'r'))
		lib["library"].append({"addedBy":who, "added":int(time.time()), "text":text})
		self.bot.do_privmsg(channel, "Thanks for the info, %s." % who)
		yaml.dump(lib, file(self.ymlPath, 'w'))