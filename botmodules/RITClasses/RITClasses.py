#! /usr/bin/env python
from botlibs import ModuleBase,SimpleConfigReader,BeautifulSoup
import re
import threading
import mechanize
from urllib import urlencode
import HTMLParser

class RITClasses(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="RITClasses"
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.do_lookup_class)]
		print "RITClasses loaded"
	def do_lookup_class(self, args, prefix, trailing):
		# pass query to the http fetcher - threaded to avoid holdups
		if trailing.startswith("!sis"):
			words = trailing.split(' ')
			if len(words)>=2:
				classid = words[1];
				print "RITClasses: checking class %s" % classid
				threadedFetcher(classid, args[0], self.bot)

class threadedFetcher(threading.Thread):
	def __init__(self, classnum, channel, bot):
		threading.Thread.__init__(self);
		self.classnum = classnum
		self.query = classnum
		self.channel=channel
		self.bot=bot
		self.start()
	def run(self):
		# make sure we have a valid course number (or course num and section)
		if re.match(r'^([0-9]{7}|[0-9]{9})$', self.classnum):
			self.collegenum = self.query[0:4]
			self.classnum = self.query[4:7]
			# hard-coded to next quarter for now... fetch the data
			allclasses = self.fetchPage("20112", str(self.collegenum));
			if len(self.query)==7:
				# spit out all of a classes sections
				if self.classnum in allclasses:
					for sect in allclasses[self.classnum]:
						self.bot.do_privmsg(self.channel, self.classdata_to_human(allclasses[self.classnum][sect]))
				else:
					self.bot.do_privmsg(self.channel, "That class doesn't exist!")
			elif len(self.query)==9:
				# spit out just one section
				self.classsect = self.query[7:9]
				if self.classnum in allclasses:
					if self.classsect in allclasses[self.classnum]:
						self.bot.do_privmsg(self.channel, self.classdata_to_human(allclasses[self.classnum][self.classsect]))
					else:
						self.bot.do_privmsg(self.channel, "That class exists, but that section does not!")
				else:
					self.bot.do_privmsg(self.channel, "That class doesn't exist!")
		else:
			self.bot.do_privmsg(self.channel, "Valid usage: !sis <classnumber> (9 or 7 digits)")
	def classdata_to_human(self,clss):
		# formats a course to a nice string
		return "%s-%s-%s: %s/%s seats. (%s with Prof %s)." % (clss["college"], clss["number"], clss["section"], clss["studentstotal"], clss["studentsmax"], clss["title"], clss["prof"])
	def fixcaps(self, str):
		# capitalizes the first letter of every word in a string
		product=[]
		for word in str.split(" "):
			product.append(word.capitalize())
		return ' '.join(product)
	def removenbsp(str, word):
		#converts &nbsp; to a space, removes duplicate spaces
		word=word.replace("&nbsp;", " ")
		while "  " in word:
			word=word.replace("  ", " ")
		return word.strip()
	# queries the SIS for a discipline, returns a Dict of courses, sections, and time
	def fetchPage(self, term, discipline):
		# enable cookie tracking
		cookies = mechanize.CookieJar()
		opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cookies))
		try:
			# initial cookie
			req = opener.open("https://sis.rit.edu/info/info.do?init=openCourses")
			# save term in cookie
			req = opener.open("https://sis.rit.edu/info/setTerm.do?source=open&init=openCourses", urlencode({"term":term}))
			# select the discipline
			req = opener.open("https://sis.rit.edu/info/getOpenCourseList.do?init=openCourses", urlencode({"discipline":discipline}))
			text = resp = req.read();
			print "RITClasses: http complete"
		except:
			self.bot.do_privmsg(self.channel, "Error Contacting SIS!")
		# chop off all but the important section
		text = text[text.find("<!-- beginOpenCourseList --> "):]
		text = text[0:text.find("<!-- endOpenCourseList --> ")]
		
		# parse the html
		bs = BeautifulSoup.BeautifulSoup(text)
		
		# save stuff i here for now
		classes = {}
		extrahours = {}
		
		# extract classes from the html
		bs = bs.find("tbody");
		lastclass = ""
		if bs:
			# for every row we...
			for tablerow in bs.findAll("tr"):
				cells = tablerow.findAll("td")
				theclass=[]
				if len(cells)==10:
					# look at every cell if it's a class row, and save the values to a List, and that list to a Class
					for cellid in range(1,len(cells)-1):
						cell = cells[cellid]
						contents = cell.contents[0]
						theclass.append(contents.strip())
					theclass.append(cells[9].a.contents[0].strip())
					theclass.append(cells[9].contents[2].strip())
					classes[cells[0].a.contents[0].strip()]=theclass
					lastclass=str(cells[0].a.contents[0].strip())
				
				else:
					# or if the row is just a secondary room/time for the course, save it to Extrahours
					for cellid in range(1,len(cells)-1):
						cell = cells[cellid]
						contents = cell.contents[0]
						theclass.append(contents.strip())
					theclass.append(cells[4].a.contents[0].strip())
					theclass.append(cells[4].contents[2].strip())
					if not lastclass in extrahours:
						extrahours[lastclass]=[]
					extrahours[lastclass].append(theclass)
		
		# get rid of that final parser and convert the data from above to a friendly format
		del bs
		finalclasses={}
		for classnumber in classes:
			classnum = classnumber[0:3];
			classsectiion = classnumber[4:6]
			info = {}
			info["college"]=discipline
			info["number"]=classnum
			info["section"]=classsectiion
			info["title"]=self.fixcaps(classes[classnumber][0].replace(":", " "))
			info["prof"]=self.fixcaps(classes[classnumber][1])
			info["status"]=self.removenbsp(classes[classnumber][2])
			info["studentsmax"]=self.removenbsp(classes[classnumber][3])
			info["studentstotal"]=self.removenbsp(classes[classnumber][4])
			info["location"]=[]
			
			temp = {}
			
			temp["days"]=classes[classnumber][5]
			temp["timestart"]=classes[classnumber][6]
			temp["timeend"]=classes[classnumber][7]
			temp["building"]=classes[classnumber][8]
			temp["room"]=classes[classnumber][9]
			
			info["location"].append(temp)
			
			for classnumberextra in extrahours:
				if classnumberextra==classnumber:
					for hourblock in extrahours[classnumberextra]:
						temp={}
						temp["days"]=hourblock[0]
						temp["timestart"]=hourblock[1]
						temp["timeend"]=hourblock[2]
						temp["building"]=hourblock[3]
						temp["room"]=hourblock[4]
						
						info["location"].append(temp)
			if not classnum in finalclasses:
				finalclasses[classnum]={}
			finalclasses[classnum][classsectiion]=info
		return finalclasses;


