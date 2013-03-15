#!/usr/bin/env python

from botlibs import ModuleBase,Tools
import datetime
import time
import math

class Calc(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="Calc"
		self.loadConfig()
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.calc)]
		self.timers={}
		
		self.sql = self.bot.getmodulesbyservice("mysql")
		if len(self.sql)==0:
			print "MySQL service is required."
			self.bot.deportmodule(self.moduleName)
			return
		self.sql = self.sql[0].getConnection()
		if not self.sql.tableExists("calc_words"):
			# TODO auto-create DB
			pass
		print "Calc loaded"
	
	def timeSince(self, channel, timetype):
		if not channel in self.timers:
			self.createDefaultTimers(channel)
		return time.time()-self.timers[channel][timetype]
	
	def updateTimeSince(self, channel, timetype):
		if not channel in self.timers:
			self.createDefaultTimers(channel)
		self.timers[channel][timetype] = time.time()
	
	def createDefaultTimers(self, channel):
		self.timers[channel]={"add":0, "calc":0, "calcspec":0, "match":0}
	
	def remainingToStr(self, total, elasped):
		remaining = total-elasped
		minutes = int(math.floor(remaining/60))
		seconds = int(remaining - (minutes*60))
		return "Please wait %s minute(s) and %s second(s)." % (minutes, seconds)
	
	def calc(self, args, prefix, trailing):
		# Channel only
		if not args[0][0]=="#":
			return
		
		if trailing[0:4]=="calc":
			calcCmd = trailing[4:]
			if "=" in calcCmd[1:]:
				" Add a new calc "
				calcWord, calcDefinition = calcCmd[1:].split("=", 1)
				calcWord = calcWord.strip()
				calcDefinition = calcDefinition.strip()
				if self.config["allowDelete"] and calcDefinition == "":
					result = self.deleteCalc(args[0], calcWord)
					if result:
						self.bot.do_privmsg(args[0], "Calc deleted, %s." % self.bot.extract_nick_from_prefix(prefix))
					else:
						self.bot.do_privmsg(args[0], "Sorry %s, I don't know what '%s' is." % (self.bot.extract_nick_from_prefix(prefix), calcWord))
				else:
					if self.config["delaySubmit"]>0 and self.timeSince(args[0], "add") < self.config["delaySubmit"]:
						self.bot.do_privmsg(self.bot.extract_nick_from_prefix(prefix), self.remainingToStr(self.config["delaySubmit"], self.timeSince(args[0], "add")))
					else:
						self.addNewCalc(args[0], calcWord, calcDefinition, prefix)
						self.bot.do_privmsg(args[0], "Thanks for the info, %s." % self.bot.extract_nick_from_prefix(prefix))
						self.updateTimeSince(args[0], "add")
			elif len(calcCmd[1:])>0:
				" Lookup the word in calcCmd "
				
				if self.config["delayCalcSpecific"]>0 and self.timeSince(args[0], "calcspec") < self.config["delayCalcSpecific"]:
					self.bot.do_privmsg(self.bot.extract_nick_from_prefix(prefix), self.remainingToStr(self.config["delayCalcSpecific"], self.timeSince(args[0], "calcspec")))
				else:
					calcCmd = calcCmd[1:]
					randCalc = self.getSpecificCalc(args[0], calcCmd)
					if randCalc==None:
						self.bot.do_privmsg(args[0], "Sorry %s, I don't know what '%s' is." % (self.bot.extract_nick_from_prefix(prefix), calcCmd))
					else:
						self.bot.do_privmsg(args[0], "%s \x03= %s \x0314[added by: %s]" % (randCalc["word"].upper(), randCalc["definition"], randCalc["by"]))
						self.updateTimeSince(args[0], "calcspec")
			else:
				if self.config["delayCalc"]>0 and self.timeSince(args[0], "calc") < self.config["delayCalc"]:
					self.bot.do_privmsg(self.bot.extract_nick_from_prefix(prefix), self.remainingToStr(self.config["delayCalc"], self.timeSince(args[0], "calc")))
				else:
					randCalc = self.getRandomCalc(args[0])
					if randCalc == None:
						self.bot.do_privmsg(args[0], "This channel has no calcs, %s :(" % (self.bot.extract_nick_from_prefix(prefix)))
					else:
						self.bot.do_privmsg(args[0], "%s \x03= %s \x0314[added by: %s]" % (randCalc["word"].upper(), randCalc["definition"], randCalc["by"]))
						self.updateTimeSince(args[0], "calc")
			return
		
		if trailing[0:5]=="match":
			if self.config["delayMatch"]>0 and self.timeSince(args[0], "match") < self.config["delayMatch"]:
				self.bot.do_privmsg(self.bot.extract_nick_from_prefix(prefix), self.remainingToStr(self.config["delayMatch"], self.timeSince(args[0], "match")))
			else:
				term = trailing[6:]
				if term.strip()=='':
					return
				c = self.sql.getCursor()
				channelId = self.getChannelId(args[0])
				c.execute("SELECT * FROM `calc_words` WHERE `word` LIKE '%%%s%%' AND `channel`=%s ORDER BY `word` ASC ;"%(self.sql.escape(term), channelId))
				if c.rowcount==0:
					self.bot.do_privmsg(args[0], "%s: Sorry, no matches" % (self.bot.extract_nick_from_prefix(prefix)))
				else:
					matches = []
					while len(matches)<10:
						row = c.fetchone()
						if row == None:
							break
						matches.append(row["word"])
					self.bot.do_privmsg(args[0], "%s: %s match%s (%s\x03)" % (self.bot.extract_nick_from_prefix(prefix), len(matches), "es" if len(matches)>1 else "", ", \x03".join(matches) ))
					self.updateTimeSince(args[0], "match")
				
	def addNewCalc(self, channel, word, definition, prefix):
		fromWho = self.bot.extract_nick_from_prefix(prefix)
		fromIp = self.bot.extract_ip_from_prefix(prefix)
		
		" Find the channel ID"
		channelId = self.getChannelId(channel)
		
		" Check if we need to add a user"
		c = self.sql.getCursor()
		name = self.bot.extract_nick_from_prefix(prefix)
		host = self.bot.extract_ip_from_prefix(prefix)
		c.execute("SELECT * FROM `calc_addedby` WHERE `username`=%s AND `userhost`=%s ;", (name, host))
		if c.rowcount==0:
			c.execute("INSERT INTO `calc_addedby` (`username`, `userhost`) VALUES (%s, %s) ;", (name, host,))
			c.execute("SELECT * FROM `calc_addedby` WHERE `username`=%s AND `userhost`=%s ;", (name, host))
		addedId = c.fetchone()["id"]
		
		" Check if the word exists"
		c.execute("SELECT * FROM `calc_words` WHERE `channel`=%s AND `word`=%s ;", (channelId, word))
		if c.rowcount==0:
			c.execute("INSERT INTO `calc_words` (`channel`, `word`, `status`) VALUES (%s, %s, %s) ;", (channelId, word, 'approved'))
			c.execute("SELECT * FROM `calc_words` WHERE `channel`=%s AND `word`=%s ;", (channelId, word))
		wordId = c.fetchone()["id"]
		" Add definition "
		c.execute("INSERT INTO `calc_definitions` (`word`, `definition`, `addedby`, `date`, `status`) VALUES (%s, %s, %s, %s, %s) ;", (wordId, definition, addedId, datetime.datetime.now(), 'approved',))
		c.close()
		pass
	
	def getSpecificCalc(self, channel, word):
		c = self.sql.getCursor()
		channelId = self.getChannelId(channel)
		c.execute("SELECT `cw`.`word`, (SELECT `cdq`.`id` FROM `calc_definitions` `cdq` WHERE `cdq`.`word`=`cw`.`id` AND `cdq`.`status`='approved' ORDER BY `cdq`.`date` DESC LIMIT 1) as `definitionId` FROM `calc_words` `cw` WHERE `cw`.`channel`=%s AND `cw`.`status`='approved' AND `cw`.`word`=%s ORDER BY RAND() LIMIT 1 ;", (channelId, word))
		word = c.fetchone()
		
		if word == None:
			return None
		
		c.execute("SELECT `ca`.`username`, `cd`.`definition` FROM `calc_definitions` `cd` JOIN `calc_addedby` `ca` ON `ca`.`id` = `cd`.`addedby` WHERE `cd`.`id`=%s LIMIT 1 ;", (word["definitionId"], ))
		
		who = c.fetchone()
		
		c.close()
		return {"word":word["word"], "definition":who["definition"], "by":who["username"]}
		
	
	def getRandomCalc(self, channel):
		c = self.sql.getCursor()
		channelId = self.getChannelId(channel)
		c.execute("SELECT `cw`.`word`, (SELECT `cdq`.`id` FROM `calc_definitions` `cdq` WHERE `cdq`.`word`=`cw`.`id` AND `cdq`.`status`='approved' ORDER BY `cdq`.`date` DESC LIMIT 1) as `definitionId` FROM `calc_words` `cw` WHERE `cw`.`channel`=%s AND `cw`.`status`='approved' ORDER BY RAND() LIMIT 1 ;", (channelId,))
		word = c.fetchone()
		if word == None:
			return None
		c.execute("SELECT `ca`.`username`, `cd`.`definition` FROM `calc_definitions` `cd` JOIN `calc_addedby` `ca` ON `ca`.`id` = `cd`.`addedby` WHERE `cd`.`id`=%s LIMIT 1 ;", (word["definitionId"], ))
		
		who = c.fetchone()
		
		c.close()
		return {"word":word["word"], "definition":who["definition"], "by":who["username"]}
	
	def deleteCalc(self, channel, word):
		" Return true if deleted something, false if it doesnt exist"
		c = self.sql.getCursor()
		channelId = self.getChannelId(channel)
		c.execute("SELECT * FROM `calc_words` WHERE `channel`=%s and `word`=%s ;", (channelId, word))
		if c.rowcount==0:
			c.close()
			return False
		
		wordId = c.fetchone()["id"]
		
		c.execute("DELETE FROM `calc_words` WHERE `id`=%s ;", (wordId,))
		c.execute("DELETE FROM `calc_definitions` WHERE `word`=%s ;", (wordId,))
		
		c.close()
		return True
	
	def getChannelId(self, channel):
		c = self.sql.getCursor()
		c.execute("SELECT * FROM `calc_channels` WHERE `channel` = %s", (channel,))
		if c.rowcount==0:
			c.execute("INSERT INTO `calc_channels` (`channel`) VALUES (%s);", (channel,))
			c.execute("SELECT * FROM `calc_channels` WHERE `channel` = %s", (channel,))
		
		chId = c.fetchone()["id"]
		c.close()
		return chId
	
