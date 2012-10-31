#!/usr/bin/env python
from botlibs import ModuleBase
from botlibs import Tools
from urllib import urlencode
import json
import urllib2
import random

class GoogleImages(ModuleBase.ModuleBase):
	def __init__(self, bot):
		# init hte base module
		ModuleBase.ModuleBase.__init__(self, bot);
		# the NAME of this module
		self.moduleName="GoogleImages"
		# hook our local method "repeat" to the "PRIVMSG" hook
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.images)]
		# let the user know we've loaded
		print "GoogleImages loaded"
	def images(self, args, prefix, trailing):
		cmd = Tools.messageHasCommand(".images", trailing)
		if cmd:
			sender = self.bot.extract_nick_from_prefix(prefix)
			query = cmd[2]
			results = self.googleImagesSearch(query)
			if len(results) == 0:
				self.bot.do_privmsg(args[0], "%s: No Results " % sender)
			else:
				chosenOne = results[random.randint(0, len(results)-1)];
				self.bot.do_privmsg(args[0], "%s: Google Image for '%s': %s " % (sender, query, chosenOne["imageUrl"]));
	def googleImagesSearch(self, query):
		f = urllib2.urlopen("https://ajax.googleapis.com/ajax/services/search/images?%s" % urlencode({"q":query, "v":1.0, "safe":"on"}))
		data = f.read()
		data = json.loads(data)
		results = []
		for result in data["responseData"]["results"]:
			results.append({"title":result["titleNoFormatting"], "imageUrl":result["unescapedUrl"]})
		return results