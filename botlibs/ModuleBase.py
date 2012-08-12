#!/usr/bin/env python

import os
import yaml

# base class which modules will extend.
class ModuleBase:
	# main will be a ref to the main bot
	def __init__(self, main):
		self.moduleName="ModuleBase"
		self.bot = main
		self.hooks=[]
		self.properties={}
		self.config={}
	def loadConfig(self):
		if os.path.exists( "botconfig/%s.yml" % (self.moduleName) ):
			self.config = yaml.load(file("botconfig/%s.yml" % (self.moduleName), 'r'))
	def loadCustomConfig(self, name):
		if os.path.exists( "botconfig/%s" % (self.moduleName) ):
			return yaml.load(file("botconfig/%s" % (self.moduleName), 'r'))
		return {}
	def getHooks(self):
		return self.hooks
	def ondisable(self):
		print "Module %s is being disabled" % self.moduleName
	def getModulePath(self):
		return "botmodules/%s/" % self.moduleName
	def getFilePath(self, file):
		if not os.path.exists("botdata/%s" % self.moduleName):
			os.makedirs("botdata/%s" % self.moduleName)
		return "botdata/%s/%s" % (self.moduleName, file)
	def log(self, message):
		print "[%s] %s" % (self.moduleName, message)
class ModuleHook:
	def __init__(self, hook, method):
		self.hook=hook
		self.method=method