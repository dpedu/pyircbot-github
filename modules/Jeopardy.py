#! /usr/bin/env python
from botlibs import ModuleBase
import Image
import ImageFont
import ImageDraw
import ImageFilter
import time
import yaml

class Jeopardy(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="Jeopardy"
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.mkimage)]
		#self.config = SimpleConfigReader.readConfig("botmodules/Jeopardy/config.txt");
		self.loadConfig()
		print "Jeopardy loaded"
	def mkimage(self, args, prefix, trailing):
		# check if message is from a channel, has a value, and pass to image function
		if args[0][0] == "#":
			if trailing[0:4]==".jeo" and len(trailing[5:])>0:
				#print "Jeopardy: Jeoing: "+trailing
				url = self.createImage(trailing[5:].upper())
				self.bot.do_privmsg(args[0], self.config["clueline"] % url)
	def createImage(self, text):
		# elimnate any extra spaces, convert to a List of words
		while "  " in text:
			text=text.replace('  ', ' ')
		jeotext = text.split(' ')
		numwords = len(jeotext)
		
		# lines drawn to the iamge will be stored here
		lines = []
		
		# load font
		font = ImageFont.truetype(self.getFilePath("scakorinnabold.ttf"), 30)
		
		# as long as we sitll have words left...
		while numwords > 0:
			section = numwords
			# chop them off until they will fit in the image
			while font.getsize(self.listwords(jeotext[:], section))[0] > 360:
				section-=1
				if section==0:
					section=1
					break
			numwords -= section
			# and save that line to our List
			lines.append(self.listwords(jeotext, section))
		
		# one line would be in the exact center of the image, so calculate how high our first line will be
		startY = 143-(len(lines)*33)/2
		
		# create image, blue background (why does PIL have R and B values swapped?)
		i = Image.new("RGB", (400, 300), 0xCC3300)
		draw = ImageDraw.Draw(i)
		
		# draw althe text a bit offset, and in blacl k
		for line in lines:
			x = 200-font.getsize(line)[0]/2
			draw.text((x+5, startY+5), line, font=font, fill=0x000000)
			startY+=33
		
		# blur the image to create text shadow
		for x in range(0,4):
			i = i.filter(ImageFilter.BLUR)
		
		# draw the text again in white
		startY=143-(len(lines)*33)/2 
		draw = ImageDraw.Draw(i)
		for line in lines:
			x = 200-font.getsize(line)[0]/2
			draw.text((x, startY), line, font=font, fill=0xFFFFFF)
			startY+=33
		
		# name the image the current time (for uniqueness)
		name = str(time.time()).replace(".", "")+".png"
		#print "Jeopardy: saving image to: %s" % self.config.imagedir+"/"+name
		i.save(self.config["imagedir"]+"/"+name, "PNG");
		return name;
	def listwords(self, list, numwords):
		# return a string from a List of words, limited to numwords words
		ret = ""
		while numwords > 0 and len(list)>0:
			numwords-=1
			ret+=list.pop(0)+" "
		return ret.strip()
