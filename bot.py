#! /usr/bin/env python
import socket
import threading
import sys
import yaml
from botlibs import *

# Experimental 
try:
	from gevent import monkey;
	monkey.patch_all()
except:
	pass;

# main class of the bot - yes, this means you can theoretically run more then one bot at once. you just need multiple config files.
class bot(threading.Thread):
	def __init__(self, configpath):
		threading.Thread.__init__(self)
		
		# path to our configuration file
		self.configpath = configpath
		
		# will hold our config information as an object
		self.config = None;
		
		# listener thread
		self.listener = None;
		
		# BufferedConnection reference
		self.connection = None;
		
		# commands from RFC 1459
		self.hooks = [
			'NOTICE',	# :irc.129irc.com NOTICE AUTH :*** Looking up your hostname...
			'MODE',		# :CloneABCD MODE CloneABCD :+iwx
			'PING',		# PING :irc.129irc.com
			'JOIN',		# :CloneA!dave@hidden-B4F6B1AA.rit.edu JOIN :#clonea
			'PART',		# :CloneA!dave@hidden-B4F6B1AA.rit.edu PART #clonea
			'PRIVMSG',	# :CloneA!dave@hidden-B4F6B1AA.rit.edu PRIVMSG #clonea :aaa
			'KICK',		# :xMopxShell!~rduser@host KICK #xMopx2 xBotxShellTest :xBotxShellTest
			'001',		# :irc.129irc.com 001 CloneABCD :Welcome to the 129irc IRC Network CloneABCD!CloneABCD@djptwc-laptop1.rit.edu
			'002',		# :irc.129irc.com 002 CloneABCD :Your host is irc.129irc.com, running version Unreal3.2.8.1
			'003',		# :irc.129irc.com 003 CloneABCD :This server was created Mon Jul 19 2010 at 03:12:01 EDT
			'004',		# :irc.129irc.com 004 CloneABCD irc.129irc.com Unreal3.2.8.1 iowghraAsORTVSxNCWqBzvdHtGp lvhopsmntikrRcaqOALQbSeIKVfMCuzNTGj
			'005',		# :irc.129irc.com 005 CloneABCD CMDS=KNOCK,MAP,DCCALLOW,USERIP UHNAMES NAMESX SAFELIST HCN MAXCHANNELS=10 CHANLIMIT=#:10 MAXLIST=b:60,e:60,I:60 NICKLEN=30 CHANNELLEN=32 TOPICLEN=307 KICKLEN=307 AWAYLEN=307 :are supported by this server
						# :irc.129irc.com 005 CloneABCD MAXTARGETS=20 WALLCHOPS WATCH=128 WATCHOPTS=A SILENCE=15 MODES=12 CHANTYPES=# PREFIX=(qaohv)~&@%+ CHANMODES=beI,kfL,lj,psmntirRcOAQKVCuzNSMTG NETWORK=129irc CASEMAPPING=ascii EXTBAN=~,cqnr ELIST=MNUCT :are supported by this server
			'251',		# :irc.129irc.com 251 CloneABCD :There are 1 users and 48 invisible on 2 servers
			'252',		# :irc.129irc.com 252 CloneABCD 9 :operator(s) online
			'254',		# :irc.129irc.com 254 CloneABCD 6 :channels formed
			'255',		# :irc.129irc.com 255 CloneABCD :I have 42 clients and 1 servers
			'265',		# :irc.129irc.com 265 CloneABCD :Current Local Users: 42  Max: 47
			'266',		# :irc.129irc.com 266 CloneABCD :Current Global Users: 49  Max: 53
			'332',		# Channel topic - :availo.esper.net 332 xBotxShell #hcsmp :Channel Title Here
			'333',		# Channel topic set date - :availo.esper.net 333 xBotxShell #hcsmp sav!savoie@irc.hcsmp.com 1343632267
			'353',		# :irc.129irc.com 353 CloneABCD = #clonea :CloneABCD CloneABC 
			'366',		# :irc.129irc.com 366 CloneABCD #clonea :End of /NAMES list.
<<<<<<< .mine
			'372',		# MOTD - :aperture.esper.net 372 xBotxShell :-                          Enjoy your stay
			'375',		# MOTD Start - :availo.esper.net 375 xBotxShell :- availo.esper.net Message of the Day -
			'376',		# MOTD End - :availo.esper.net 376 xBotxShell :End of /MOTD command.
=======
			'372',		# :chaos.esper.net 372 xBotxShell :motd text here
			'376',		# :chaos.esper.net 376 xBotxShell :End of /MOTD command.
>>>>>>> .r26
			'422'		# :irc.129irc.com 422 CloneABCD :MOTD File is missing
		]
		# /me is :user PRIVMSG #clonea :ACTION action
		
		# map of commands to hooked-in methods - created automatically
		self.hookcalls = {}
		
		# stored imported modules
		self.modules = {}
		
		# instances of modules
		self.moduleInstances = {}
		
		# module settings that persist across reload
		self.moduleSettings = {}
		
	def start(self):
		# load bots configuration
		self.readConfig()
		# create dict of hookable functions
		self.createHookCalls()
		# from the config, load all the autoloaded modules
		self.loadInitialModules()
		# Conenct to server
		self.connect()
		# Send USER and NICK and that crap
		self.initConnection()
		# Start out listener thread
		self.listener = botListener(self)
	
	def connect(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(( self.config["server"], int(self.config["port"]) ))
		self.connection = BufferedConnection.BufferedConnection(s)
	
	def readConfig(self):
		self.config = yaml.load(file(self.configpath, 'r'))
	
	def initConnection(self):
		self.sendUser()
		self.set_nick(self.config["nick"])
	
	def createHookCalls(self):
		for command in self.hooks:
			self.hookcalls[command]=[]
		
	def addHook(self, command, method):
		if command in self.hooks:
			self.hookcalls[command].append(method);
		else:
			print "Invalid hook - %s" % command
			return False
	
	def removeHook(self, command, method):
		if command in self.hooks:
			for hookedMethod in self.hookcalls[command]:
				if hookedMethod == method:
					self.hookcalls[command].remove(hookedMethod)
		else:
			print "Invalid hook - %s" % command
			return False
	
	def loadModuleHooks(self, module):
		for hook in module.hooks:
			self.addHook(hook.hook, hook.method)
	
	def unloadModuleHooks(self, module):
		for hook in module.hooks:
			self.removeHook(hook.hook, hook.method)
	def loadInitialModules(self):
		for modulename in self.config["autoload"]:
			self.loadmodule(modulename)
	
	def loadmodule(self, name):
		if name in self.moduleInstances:
			print "Module %s already loaded" % name
			return false
		if not name in self.modules:
			self.importmodule(name)
		self.moduleInstances[name] = getattr(self.modules[name], name)(self)
		self.loadModuleHooks(self.moduleInstances[name])
		if name in self.moduleSettings:
			moduleInstances[name].properties = self.moduleSettings[name]
	def unloadmodule(self, name):
		if name in self.moduleInstances:
			# run module's diable method
			self.moduleInstances[name].ondisable()
			# remove hooks
			self.unloadModuleHooks(self.moduleInstances[name]);
			# remove instance in self.moduleInstances
			item = self.moduleInstances.pop(name)
			# and finally, delete the object.
			del item
			print "Module %s unloaded" % name
		else:
			print "module %s not loaded" % name
	def importmodule(self, name):
		if not name in self.modules:
			try:
				# add the path to this module so python can find it
				sys.path.append("botmodules/"+name)
				# manually import the module saving it in out list of modules
				moduleref = __import__(name)
				self.modules[name]=moduleref
				return True
			except Exception, e:
				print "Module %s failed to load: " % name
				print str(e)
				return False
		else:
			print "Module %s already imported" % name
			return False
		# this will silently fail if the module is already loaded
	def deportmodule(self, name):
		# unload it before we do this
		self.unloadmodule(name)
		if name in self.modules:
			# delete it
			item = self.modules[name];
			del self.modules[name]
			del item
			# and remove it's path from $PYTHONPATH
			sys.path.remove("botmodules/"+name)
			# finally, delete any cache in sys.modules
			del sys.modules[name]
	def reloadmodule(self, name):
		if name in self.modules:
			loadedbefore = name in self.moduleInstances;
			self.unloadmodule(name);
			print "reloading %s" % self.modules[name]
			reload(self.modules[name])
			if loadedbefore:
				self.loadmodule(name);
	def redomodule(self, name):
		loadedbefore = name in self.moduleInstances;
		self.deportmodule(name)
		self.importmodule(name)
		if loadedbefore:
			self.loadmodule(name)
	
	def set_nick(self, newNick):
		self.sendText("NICK %s" % newNick);
	def get_nick(self):
		return self.config["nick"];
	
	def do_join(self, channel):
		self.sendText("JOIN %s"%channel);
		
	def do_privmsg(self, towho, message):
		self.sendText("PRIVMSG %s :%s"%(towho,message))
		
	def do_pingrespond(self, where):
		self.sendText("PONG :%s" % where)
	
	def do_action(self, channel, action):
		self.sendText("PRIVMSG %s :\x01ACTION %s"%(channel,action))
		
	def do_kick(self, channel, who, comment):
		self.sendText("KICK %s %s :%s" % (channel, who, comment));
	
	
	def sendUser(self):
		self.sendText("USER %s %s %s :%s" % (self.config["nick"], self.config["hostname"], self.config["server"], self.config["realname"]))
	
	def sendText(self, text):
		self.connection.send(text+"\n")
	
	def extract_nick_from_prefix(self, prefix):
		pos=[]
		pos.append(prefix.find("@"))
		pos.append(prefix.find("!"))
		pos.sort()
		return prefix[0:pos[0]]
	def processLine(self, line):
		if line.strip() == "":
			return;
		originalline = line
		prefix = None;
		command = None
		args=[]
		trailing=None
		
		if line[0]==":":
			prefix=line.split(" ")[0][1:]
			line=line[line.find(" ")+1:]
		command = line.split(" ")[0]
		line=line[line.find(" ")+1:]
		if(line[0]==":"):
			# no args
			trailing = line[1:].strip()
		else:
			trailing = line[line.find(" :")+2:].strip()
			line = line[:line.find(" :")]
			args = line.split(" ")
		for index,arg in enumerate(args):
			args[index]=arg.strip()
		#print "Got cmd '%s' prefix '%s' args '%s', trailing '%s'" % (command, prefix, args, trailing)
		if not command in self.hookcalls:
			print "Unknown command: cmd='%s' prefix='%s' args='%s' trailing='%s'" % (command, prefix, args, trailing)
			print "Original text: '%s'" % (originalline.strip())
		else:
			for hook in self.hookcalls[command]:
				hook(args, prefix, trailing)
		
class botListener(threading.Thread):
	def __init__(self, bot):
		threading.Thread.__init__(self)
		self.bot = bot;
		self.start()
	
	def run(self):
		while 1:
			line=self.bot.connection.nextLine()
			self.bot.processLine(line);

botThread = bot("botconfig/config.yml")
botThread.start()

while 1:
	c = raw_input().strip();
	try:
		args = c.split(" ")
		if args[0]=="load":
			botThread.loadmodule(args[1])
		elif args[0]=="unload":
			botThread.unloadmodule(args[1])
		elif args[0]=="dump":
			if args[1]=="imports":
				print str(botThread.modules)
			elif args[1]=="insts":
				print str(botThread.moduleInstances)
			elif args[1]=="hookcalls":
				print str(botThread.hookcalls)
			elif args[1]=="settings":
				print str(botThread.moduleSettings)
			elif args[1]=="modules":
				for item in sys.modules:
					print "%s: %s" % (item, sys.modules[item])
		elif args[0]=="deport":
			botThread.deportmodule(args[1]);
		elif args[0]=="import":
			botThread.importmodule(args[1]);
		elif args[0]=="reload":
			botThread.reloadmodule(args[1]);
		elif args[0]=="redo":
			botThread.redomodule(args[1]);
		else:
			print "nope"
	except:
		pass
