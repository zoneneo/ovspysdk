import sqlite3

class Sqlite_Manager():
	def __init__(self):
		self.coon = sqlite3.connect('networkmaindb.db')
		
	def getCoon(self):
		self.coon = sqlite3.connect('networkmaindb.db')
		return self.coon
		
	def selectNetworkWithName(self,networkname):
		cx = self.getCoon()
		cu = cx.execute("SELECT * FROM NETWORKTABLE WHERE NETWORKNAME ='"+networkname+"';")
		rows = cu.fetchall()
		cx.close()
		return rows	
		
	def addNetwork(self,networktype,username,servicename,networkname):
		cx = self.getCoon()
		cu=cx.cursor()
		v = (networktype,username,servicename,networkname)
		ins = "INSERT INTO NETWORKTABLE(NETWORKTYPE,USERNAME,SERVICENAME,NETWORKNAME) VALUES (?,?,?,?);"
		cu.execute(ins,v)
		cx.commit()
		cx.close()
		
	def getNetworkWithNetworkName(self,networkname):
		cx = self.getCoon()
		cu = cx.execute("SELECT * FROM NETWORKTABLE WHERE NETWORKNAME ='"+networkname+"';")
		rows = cu.fetchall()
		cx.close()
		return rows	
		
	def delNetwork(self,networktype,networkname):
		try:
			cx = self.getCoon()
			cx.execute("DELETE FROM NETWORKTABLE WHERE NETWORKTYPE ='"+networktype+"' AND NETWORKNAME ='"+networkname+"';")
			cx.commit()
			cx.close()
		except:
			return 'error'
		else:
			return 'success'
		
	def selectNetworkWithUserService(self,netwotktype,username,servicename):
		cx = self.getCoon()
		cu = cx.execute("SELECT * FROM NETWORKTABLE WHERE NETWORKTYPE ='"+netwotktype+"' AND USERNAME ='"+username+"' AND SERVICENAME ='"+servicename+"';")
		rows = cu.fetchall()
		cx.close()
		return rows	
		
	def addHostOvsNetwork(self,networkname,hostip):
		cx = self.getCoon()
		cu=cx.cursor()
		v = (networkname,hostip)
		ins = "INSERT INTO HOSTTABLE(NETWORKNAME,HOSTIP) VALUES (?,?);"
		cu.execute(ins,v)
		cx.commit()
		cx.close()
	
	def getHost(self,hostip,networkname):
		cx = self.getCoon()
		cu = cx.execute("SELECT * FROM HOSTTABLE WHERE HOSTIP ='"+hostip+"' AND NETWORKNAME ='"+networkname+"';")
		rows = cu.fetchall()
		cx.close()
		return rows
		
	def	getHostOvsNetwork(self,networkname):
		cx = self.getCoon()
		cu = cx.execute("SELECT * FROM HOSTTABLE WHERE NETWORKNAME ='"+networkname+"';")
		rows = cu.fetchall()
		cx.close()
		return rows	
		
	def delHostWithHostip(self,hostip,networkname):
		try:
			cx = self.getCoon()
			cx.execute("DELETE FROM HOSTTABLE WHERE HOSTIP ='"+hostip+"' AND NETWORKNAME ='"+networkname+"';")
			cx.commit()
			cx.close()
		except:
			return 'error'
		else:
			return 'success'
			
	def delHostWithNetwork(self,networkname):
		try:
			cx = self.getCoon()
			cx.execute("DELETE FROM HOSTTABLE WHERE NETWORKNAME ='"+networkname+"';")
			cx.commit()
			cx.close()
		except:
			return 'error'
		else:
			return 'success'
		
	def setTable(self):
		self.coon.execute('CREATE TABLE NETWORKTABLE \
		(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
		NETWORKTYPE TEXT NOT NULL,\
		USERNAME TEXT,\
		SERVICENAME TEXT NOT NULL,\
		NETWORKNAME TEXT NOT NULL);')

		
		self.coon.execute('CREATE TABLE HOSTTABLE \
		(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
		NETWORKNAME TEXT NOT NULL, \
		HOSTIP TEXT NOT NULL,\
		SERVICENAME TEXT);')
		self.coon.close()

