#! /usr/bin/env python
from botlibs import ModuleBase,SimpleConfigReader
from urllib import urlencode
import mechanize
import threading
import time

class Barbra(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="Barbra"
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.repeat)]
		print "Barbra loaded"
	def repeat(self, args, prefix, trailing):
		# check if message is from a channel
		if args[0][0] == "#":
			if trailing[0:7]==".barbra":
				print "barbraing: "+trailing
				BarbraThread(self.bot, args[0], trailing[7:]);

class BarbraThread(threading.Thread):
	def __init__(self, bot, channel, text):
		threading.Thread.__init__(self);
		self.bot = bot
		self.channel = channel
		self.text = text
		self.start()
	def run(self):
		# track cookies
		cookies = mechanize.CookieJar()
		opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cookies))
		# request this "hit" be made
		req = opener.open("http://gobarbra.com/tworz-hit", urlencode({"glos":"gb_brian", "tresc":self.text}))
		resp = req.read();
		# was it an immediate generation?
		if "http://gobarbra.com/hit/new-" in req.geturl():
			self.gotResult(req.geturl())
		code = ""
		tries = 0
		# try up to 5 times (25 seconds) to see if it's done
		while len(code)<10 and tries < 5:
			time.sleep(5)
			req2 = opener.open("http://gobarbra.com/is-hit-ready?elo")
			code = req2.read();
			tries+=1
		self.gotResult("http://gobarbra.com/hit/"+code);
	def gotResult(self, url):
		self.bot.do_privmsg(self.channel, "Go Barbra! - %s" % url)