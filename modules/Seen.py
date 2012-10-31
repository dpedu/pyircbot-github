#!/usr/bin/env python
from botlibs import ModuleBase,SimpleConfigReader
import sqlite3
import time

class Seen(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="Seen"
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.lastSeen)]
		self.loadConfig()
		# if the database doesnt exist, it will be created
		sql = self.getSql()
		c=sql.cursor()
		# check if our table exists
		c.execute("SELECT * FROM SQLITE_MASTER WHERE `type`='table' AND `name`='seen'")
		if len(c.fetchall())==0:
			print "Seen: created table"
			# if no, create it.
			c.execute("CREATE TABLE `seen` (`nick` VARCHAR(32), `date` INTEGER, PRIMARY KEY(`nick`))");
		print "Seen loaded"
	def lastSeen(self, args, prefix, trailing):
		# using a message to update last seen, also, the .seen query
		nick = self.bot.extract_nick_from_prefix(prefix)
		sql=self.getSql()
		c = sql.cursor()
		# update or add the user's row
		c.execute("REPLACE INTO `seen` (`nick`, `date`) VALUES (?, ?)", (nick.lower(), str( time.time()+(int(self.config["add_hours"])*60*60) )))
		sql.commit()
		if trailing.startswith(".seen"):
			cmdargs = trailing.split(" ");
			# query the DB for the user
			if len(cmdargs)>=2:
				searchnic = cmdargs[1].lower();
				c.execute("SELECT * FROM `seen` WHERE `nick`= ? ", [searchnic])
				rows = c.fetchall()
				if len(rows)==1:
					self.bot.do_privmsg(args[0], "I last saw %s on %s (%s)."% (cmdargs[1], time.strftime("%m/%d/%y at %I:%M %p", time.localtime(rows[0]['date'])), self.config["timezone"]));
				else:
					self.bot.do_privmsg(args[0], "Sorry, I haven't seen %s!" % cmdargs[1])
		c.close()
	def getSql(self):
		# return a SQL reference to the database
		sql = sqlite3.connect(self.getFilePath('database.sql3'));
		sql.row_factory = self.dict_factory
		return sql
	def dict_factory(self, cursor, row):
		# because Lists suck for database results
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d