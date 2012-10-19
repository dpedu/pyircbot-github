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
		
		self.banlist = self.config["banlist"]
		self.baniplist = []
		
		if self.config["storage"]=="yaml":
			# Check if our library YML file exists
			if not os.path.exists(self.ymlPath):
				yaml.dump({"library":[{"addedBy":"System", "added":int(time.time()), "text":"This is the default factoid.", "approved":True}]}, file(self.ymlPath, 'w'))
		elif self.config["storage"]=="mysql":
			self.sql = self.bot.getmodulesbyservice("mysql")
			if len(self.sql)==0:
				print "MySQL service is required."
				self.bot.deportmodule(self.moduleName)
				return
			self.sql = self.sql[0].getConnection()
			c = self.sql.getCursor()
			if not self.sql.tableExists("didyouknow_facts"):
				print "DidYouKnowApprove: Creating MySQL table"
				r = c.execute("""CREATE TABLE `didyouknow_facts` (
				   `id` int(11) not null auto_increment,
				   `date` int(11),
				   `user` varchar(64),
				   `ip` varchar(256),
				   `text` varchar(512),
				   `status` int(1),
				   PRIMARY KEY (`id`)
				);""")
				c.close()
			#if not sql.tableExists("didyouknow_bans"):
			#	print "DidYouKnowApprove: Creating MySQL table"
			#	r = sql.query("""CREATE TABLE `didyouknow_bans` (
			#	   `id` int(11) not null auto_increment,
			#	   `date` int(11),
			#	   `user` varchar(64),
			#	   `ip` varchar(256),
			#	   `length` int(1),
			#	   PRIMARY KEY (`id`)
			#	);""")
		print "DidYouKnowApprove loaded"
	
	def iknew(self, args, prefix, trailing):
		# Channel only
		if not args[0][0]=="#":
			return
		
		# Check banned names
		fromWho = self.bot.extract_nick_from_prefix(prefix)
		if fromWho in self.banlist:
			return;
		
		# Checked banned IPs
		fromIp = self.bot.extract_ip_from_prefix(prefix)
		if fromIp in self.baniplist:
			return
		
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
			if self.factAlreadyExists(cmd[2]):
				allowed = False
			if allowed:
				self.addFactoid(fromWho, fromIp, cmd[2].strip(), args[0])
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
	
	def factAlreadyExists(self, content):
		if self.config["storage"]=="yaml":
			lib = yaml.load(file(self.ymlPath, 'r'))
			for fact in lib["library"]:
				if fact["text"] == content.strip():
					return True
		elif self.config["storage"]=="mysql":
			c = self.sql.getCursor()
			q = c.execute("SELECT * FROM `didyouknow_facts` WHERE `text`= %s ;", ( content.strip() ))
			count = c.rowcount
			c.close()
			return count>0
		else:
			# No storage configured, block addition of this fact
			return True
	
	def loadRandomFactoid(self):
		if self.config["storage"]=="yaml":
			lib = yaml.load(file(self.ymlPath, 'r'))
			listApproved = []
			
			for fact in lib["library"]:
				if fact["approved"]:
					listApproved.append(fact)
			
			if len(listApproved)==0:
				return False
			randomFact = listApproved[random.randint(0, len(listApproved)-1)]
			return randomFact
		elif self.config["storage"]=="mysql":
			c = self.sql.getCursor()
			q = c.execute("SELECT * FROM `didyouknow_facts` WHERE `status`= 1 ORDER BY RAND() LIMIT 1 ;")
			if c.rowcount==0:
				c.close()
				return {"text":"There are no facts :("}
			fact = c.fetchone()
			c.close()
			return fact
		else:
			return {"text":"No storage for facts is configured."}
	def addFactoid(self, who, ip, text, channel):
		if self.config["storage"]=="yaml":
			lib = yaml.load(file(self.ymlPath, 'r'))
			lib["library"].append({"addedBy":who, "added":int(time.time()), "text":text, "approved":False})
			yaml.dump(lib, file(self.ymlPath, 'w'))
		elif self.config["storage"]=="mysql":
			c = self.sql.getCursor()
			q = c.execute("INSERT INTO `didyouknow_facts` (`date`, `user`, `ip`, `text`, `status`) VALUES(%s, %s, %s, %s, %s) ;", (int(time.time()), who, ip, text, 0))
			c.close()
		else:
			self.bot.do_privmsg(channel, "There is no storage configured :(")
			return 1
		self.bot.do_privmsg(channel, "Thanks for the info, %s." % who)
