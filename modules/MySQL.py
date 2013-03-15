#!/usr/bin/env python
from botlibs import ModuleBase
import MySQLdb

class MySQL(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="MySQL"
		self.hooks=[]
		self.services=["mysql"]
		self.loadConfig()
		self.connection = None
		print "MySQL loaded"
	
	def getConnection(self):
		return Connection(self.config)
	

class Connection:
	def __init__(self, config):
		self.config = config
		self._connect()
	
	# Check if the table requested exists
	def tableExists(self, tablename):
		c = self.getCursor()
		c.execute("SHOW TABLES;")
		tables = c.fetchall()
		if len(tables)==0:
			return False;
		key = tables[0].keys()[0]
		for table in tables:
			if table[key]==tablename:
				return True;
		return False
	
	def query(self, queryText, args=()):
		c = self.getCursor()
		if len(args)==0:
			c.execute(queryText)
		else:
			c.execute(queryText, args)
		return c
	
	# Returns a cusor object, after checking for connectivity
	def getCursor(self):
		self.ensureConnected()
		return self.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	
	def escape(self, s):
		self.ensureConnected()
		return self.connection.escape_string(s)
	
	def ensureConnected(self):
		try:
			self.connection.ping()
		except:
			try:
				self.connection.close()
			except:
				pass
			del self.connection
			print "MySQL: Connecting to db host at %s" % self.config["host"]
			self._connect()
	
	def ondisable(self):
		self.connection.close()
	
	# Connects to the database server, and selects a database (Or attempts to create it if it doesn't exist yet)
	def _connect(self):
		self.connection = MySQLdb.connect(host=self.config["host"],user=self.config["username"] ,passwd=self.config["password"])
		self.connection.autocommit(True)
		c = self.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
		c.execute("SHOW DATABASES")
		dblist = c.fetchall()
		found = False
		for row in dblist:
			if row["Database"]==self.config["database"]:
				found = True
		if not found:
			c.execute("CREATE DATABASE `%s`;" % self.config["database"])
		c.execute("USE `%s`;" % self.config["database"])
		c.close()