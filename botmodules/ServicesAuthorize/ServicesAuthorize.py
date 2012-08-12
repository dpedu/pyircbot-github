#!/usr/bin/env python
from botlibs import ModuleBase

class ServicesAuthorize(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="ServicesAuthorize"
		self.hooks=[
			ModuleBase.ModuleHook("376", self.authenticate),
			ModuleBase.ModuleHook("NOTICE", self.checkAuth)
		]
		self.loadConfig();
		self.properties={"Authorized":False}
		print "ServicesAuthorize loaded"
	def authenticate(self, args, prefix, trailing):
		if (self.config["auth_nick"] == "yes" or self.config["auth_nick"] == True) and self.bot.get_nick() == self.config["passwordfor"]:
			self.bot.do_privmsg("NICKSERV", "IDENTIFY %s" % self.config["password"]);
	def checkAuth(self, args, prefix, trailing):
		if args[0]==self.config["passwordfor"]:
			if "isn't registered" in trailing:
				print "%s: error: nickname not registered? t=%s" % (self.moduleName, trailing)
			elif "Password incorrect." in trailing:
				print "%s: error: password is incorrect? t=%s" % (self.moduleName, trailing) 
			elif "Password accepted" in trailing or "You are now identified for" in trailing:
				self.properties["Authorized"]=True
				print "ServicesAuthorize: Authorized Successfully."