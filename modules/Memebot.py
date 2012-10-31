#!/usr/bin/env python
from botlibs import ModuleBase
from botlibs import Tools
import Image
import ImageFont
import ImageDraw
import ImageFilter
import yaml
import time
import hashlib
import random
import os

class Memebot(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="Memebot"
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.mkimage)]
		self.loadConfig()
		
		self.banIps = [] # 'hidden-4752F170.illegalroot.net', 'hidden-1DE9476.static.optonline.net' antiroach
		
		self.memeInfoPath = self.getFilePath("base.yml")
		self.memes = self.loadCustomConfigFile(self.memeInfoPath)
		
		self.memeLibPath = self.getFilePath("library.yml")
		self.existingMemes = self.loadCustomConfigFile(self.memeLibPath)
		
		if not "memes" in self.existingMemes:
			self.existingMemes["memes"]=[]
		
		print "Memebot loaded"
	
	def mkimage(self, args, prefix, trailing):
		prefixIp = prefix.split("@")[1]
		if prefixIp in self.banIps:
			return
		
		cmd = Tools.messageHasCommand(".remove", trailing)
		if cmd and args[0][0] != "#":
			sender = self.bot.extract_nick_from_prefix(prefix)
			removeSplit = cmd[2].split(" ")
			if len(removeSplit)!=2:
				return
			password, toRemove = removeSplit
			if password!="adminPassword45678":
				self.bot.do_privmsg(sender, "Wrong password.")
				return
			removes = []
			for meme in self.existingMemes["memes"]:
				if meme["memeFile"]==toRemove:
					removes.append(meme)
			for item in removes:
				if os.path.exists( self.getFilePath("images/%s"%item["memeFile"]) ):
					os.remove( self.getFilePath("images/%s"%item["memeFile"]) )
				self.existingMemes["memes"].remove(item)
				self.bot.do_privmsg(sender, "Meme removed.")
			yaml.dump(self.existingMemes, file(self.memeLibPath, 'w'))
		
		cmd = Tools.messageHasCommand(".help", trailing)
		if cmd:
			sender = self.bot.extract_nick_from_prefix(prefix)
			
			self.bot.do_privmsg(sender, "I Am Memebot and I create meme images.")
			self.bot.do_privmsg(sender, "Commands: .help .faqs .memes .meme")
			self.bot.do_privmsg(sender, "Examples: .meme Bush Sucks   <- Create a meme with a random image")
			self.bot.do_privmsg(sender, "Examples: .memes             <- Get a list of available memes")
			self.bot.do_privmsg(sender, "Examples: .icp I eat dicks   <- Create a meme of the icp with your given text")
			return
		
		cmd = Tools.messageHasCommand(".faqs", trailing)
		if cmd:
			sender = self.bot.extract_nick_from_prefix(prefix)
			self.bot.do_privmsg(sender, "PM me .faq <number> for answers.")
			self.bot.do_privmsg(sender, "FAQ 1: You're broken! Who do I contact?")
			self.bot.do_privmsg(sender, "FAQ 2: How can I submit a new background image to the bot?")
			self.bot.do_privmsg(sender, "FAQ 3: I'm offended! How can I get an image taken down?")
			self.bot.do_privmsg(sender, "FAQ 4: Is your source code available?")
			return
		
		cmd = Tools.messageHasCommand(".faq", trailing)
		if cmd:
			sender = self.bot.extract_nick_from_prefix(prefix)
			faqnum = -1
			try:
				faqnum = int(cmd[2])
			except:
				return
				# invalid faq number
			if faqnum==1:
				self.bot.do_privmsg(sender, "Answer 1: This bot can be fixed by YourNameHere.")
			elif faqnum==2:
				self.bot.do_privmsg(sender, "Answer 2: New images should have the URL PM'd to YourNameHere.")
				self.bot.do_privmsg(sender, "Answer 2: If the demand is enough, a .suggest command may be added in the future.")
			elif faqnum==3:
				self.bot.do_privmsg(sender, "Answer 3: No images will be taken down with the exception of extreme cases and ")
				self.bot.do_privmsg(sender, "Answer 3: valueless images (such as images full of invalid characters)")
			elif faqnum==4:
				self.bot.do_privmsg(sender, "Answer 4: Memebot is a module for PyIRC bot. The bot including this module")
				self.bot.do_privmsg(sender, "Answer 4: can be found on github: https://github.com/xMopx/pyircbot-github")
		# past here is channel-only commands.
		if not args[0][0] == "#":
			return
		
		# look for an appropriate command
		for memecmd in self.memes:
			cmd = Tools.messageHasCommand(memecmd, trailing)
			if cmd:
				
				sender = self.bot.extract_nick_from_prefix(prefix)
				text = cmd[2].upper().strip()
				
				self.bot.do_privmsg(args[0], "%s: Meme created: http://yourmemehost/memes/%s" % (sender, self.getMeme(memecmd, text, prefix)))
				return
		
		cmd = Tools.messageHasCommand(".memes", trailing)
		if cmd:
			available = []
			for meme in self.memes:
				available.append(meme)
			available = ', '.join(available)
			sender = self.bot.extract_nick_from_prefix(prefix)
			self.bot.do_privmsg(sender, "Available memes: %s" % available)
			return
		
		cmd = Tools.messageHasCommand(".meme", trailing)
		if cmd:
			memecommands = self.memes.keys()
			chosen = memecommands[random.randint(0, len(memecommands)-1)]
			
			sender = self.bot.extract_nick_from_prefix(prefix)
			text = cmd[2].upper().strip()
			
			self.bot.do_privmsg(args[0], "%s: Meme created: http://yourmemehost/memes/%s" % (sender, self.getMeme(chosen, text, prefix)))
			return
	
	def getMeme(self, memecmd, text, prefix):
		sender = self.bot.extract_nick_from_prefix(prefix)
		memeExists = self.checkMemeExists(memecmd, text)
		if not memeExists:
			# choose which varient
			
			options = self.memes[memecmd]
			chosenMeme = options[random.randint(0, len(options)-1)]
			
			imageName = self.createMeme(chosenMeme, text)
			
			self.existingMemes["memes"].append( {"memecommand":memecmd, "text":text, "memeFile": imageName, "created":time.time(), "author":prefix, "authorName":sender} )
			yaml.dump(self.existingMemes, file(self.memeLibPath, 'w'))
			
			return imageName
			
		else:
			return memeExists["memeFile"]
	
	def checkMemeExists(self, meme, text):
		for item in self.existingMemes["memes"]:
			if item["memecommand"]==meme and item["text"]==text:
				return item
		return False
	
	def ondisable(self):
		yaml.dump(self.existingMemes, file(self.memeLibPath, 'w'))
		print "Module %s is being disabled" % self.moduleName
	
	def createMeme(self, memeInfo, text):
		name = hashlib.md5()
		name.update(str(time.time()))
		name = name.hexdigest()[0:6]+".jpg"
		
		# elimnate any extra spaces, convert to a List of words
		while "  " in text:
			text=text.replace("  ", " ")
		text = text.split(" ")
		
		imageLines = []
		font = ImageFont.truetype(self.getFilePath("Impact.ttf"), memeInfo["fontsize"])
		textSectionWidth = memeInfo["bound2"][0]-memeInfo["bound1"][0]
		
		while len(text) > 0:
			# the current line
			currentLine = []
			#while we're under size, remove a word from the beginning of the master list and add it to the current line
			while len(text)>0 and font.getsize(" ".join(currentLine))[0] <= textSectionWidth:
				currentLine.append(text.pop(0))
			
			currentDims = font.getsize(" ".join(currentLine));
			
			# If we're oversize, pop a word back
			if len(currentLine)>1 and currentDims[0]>=textSectionWidth:
				text.insert(0, currentLine.pop())
			
			imageLines.append(" ".join(currentLine).decode("UTF-8"))
			
		lineHeight = font.getsize("Hello.")[1];
		
		# Create image from base file
		i = Image.open(self.getFilePath("base/%s"%memeInfo["image"]))
		draw = ImageDraw.Draw(i)
		
		# draw black text outline
		for offsetX in range(memeInfo["fontsize"]/20*-1, memeInfo["fontsize"]/20+1):
			for offsetY in range(memeInfo["fontsize"]/20*-1, memeInfo["fontsize"]/20+1):
				startY = memeInfo["bound1"][1]
				for line in imageLines:
					x = memeInfo["bound1"][0]
					draw.text((x+offsetX, startY+offsetY), line, font=font, fill=0x000000)
					startY+=lineHeight
		# Draw white text
		startY = memeInfo["bound1"][1]
		# draw althe text 
		for line in imageLines:
			x = memeInfo["bound1"][0]
			draw.text((x, startY), line, font=font, fill=0xFFFFFF)
			startY+=lineHeight
		
		# Save
		i.save(self.getFilePath("images/%s"%name), "JPEG");
		
		# Return the iamge file
		return name
