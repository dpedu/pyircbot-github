#!/usr/bin/env python

from botlibs import ModuleBase,Tools
import socket
import time
import urllib2
from threading import Timer

class MojangCheck(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="MojangCheck"
		
		self.loadConfig()
		
		self.c = CheckMojangLib(self.config["mcbouncerapikey"])
		
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.checkem)]
		
		self.prefixs = {"up":"\x033+", "down":"\x034-", "slow":"\x037~"}
		self.results = {"login":False, "session":False, "web":False, "skin":False, "account":False}
		
		self.timer = Timer(5, self.pingCheck)
		self.timer.start()
		print "MojangCheck loaded"
	
	def ondisable(self):
		self.timer.cancel()
	
	def checkem(self, args, prefix, trailing):
		fromWho = self.bot.extract_nick_from_prefix(prefix)
		
		cmd = Tools.messageHasCommand("!mcstatus", trailing, False)
		if cmd and cmd[2]=='':
			
			status = "Minecraft Status " 
			if self.last_checked_at:
				status += "(%i seconds ago)" % (time.time() - self.last_checked_at) 
			status += ": "
			
			color = self.choosePrefixFor(self.results["login"])
			status+=color+"Login"+color[0:-1]+" "
			
			color = self.choosePrefixFor(self.results["session"])
			status+=color+"Session"+color[0:-1]+" "
			
			color = self.choosePrefixFor(self.results["web"])
			status+=color+"Website"+color[0:-1]+" "
			
			color = self.choosePrefixFor(self.results["skin"])
			status+=color+"Skins"+color[0:-1]+" "
			
			color = self.choosePrefixFor(self.results["account"])
			status+=color+"Accounts"+color[0:-1]+" "
			
			color = self.choosePrefixFor(self.results["mcbouncer"])
			status+=color+"MCBouncer"+color[0:-1]
			
			self.bot.do_privmsg(args[0], status)
			
	
	def choosePrefixFor(self, result):
		if result == self.c.RESULT_UP:
			return self.prefixs["up"]
		if result == self.c.RESULT_SLOW:
			return self.prefixs["slow"]
		if result == self.c.RESULT_DOWN:
			return self.prefixs["down"]
	
	def pingCheck(self):
		
		self.results = {
			"login":self.c.checkLogin(),
			"session":self.c.checkSession(),
			"web":self.c.checkWeb(),
			"skin":self.c.checkSkin(),
			"account":self.c.checkAccount(),
			"mcbouncer":self.c.checkMcbouncer()
		}
		self.last_checked_at = time.time()
		
		self.timer = Timer(25, self.pingCheck)
		self.timer.start()

class CheckMojangLib:
	
	RESULT_SLOW=1
	RESULT_UP=2
	RESULT_DOWN=3
	
	def __init__(self, mcbouncerkey):
		self.mcbouncerkey = mcbouncerkey
	
	def pingService(self, url):
		try:
			r = urllib2.Request(url)
			r = urllib2.urlopen(r, timeout=5)
			return r.read()
		except:
			return ""
	
	def checkService(self, url, expect, timeout=3):
		start = time.time()
		up = expect in self.pingService(url)
		end = time.time()
		
		if up and end-start > timeout:
			return self.RESULT_SLOW
		elif up:
			return self.RESULT_UP
		else:
			return self.RESULT_DOWN
	
	def checkLogin(self):
		return self.checkService("http://login.minecraft.net/?user=xMopx&password=&version=1", "Account migrated, use e-mail as username.", timeout=3)
	
	def checkSession(self):
		return self.checkService("http://session.minecraft.net/game/checkserver.jsp?user=xMopx&serverId=AE845FC", "NO", timeout=3)
	
	def checkWeb(self):
		return self.checkService("http://minecraft.net", "Getting started", timeout=5)
	
	def checkSkin(self):
		return self.checkService("http://minecraft.net/skin/xMopx.png", "PNG", timeout=3)
	
	def checkAccount(self):
		return self.checkService("https://account.mojang.com/terms", "terms and conditions", timeout=5)
	
	def checkMcbouncer(self):
		return self.checkService("http://mcbouncer.com/api/getBans/"+self.mcbouncerkey+"/xMopx/0/0", '{"success":true,"error":"",', timeout=3)
