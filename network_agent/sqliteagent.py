import sqlite3

class Sqlite_Agent():
	def __init__(self):
		self.coon = sqlite3.connect('networkdb.db')
		
	def getCoon(self):
		self.coon = sqlite3.connect('networkdb.db')
		return self.coon
		
	def selectOvsWithOvsip(self,ovs_ip):
		cx = self.getCoon()
		cu = cx.execute("SELECT * FROM OVSTABLE WHERE VTEPIP ='"+ovs_ip+"';")
		rows = cu.fetchall()
		cx.close()
		return rows
		
	def selectOvsWithHostname(self,host_name):
		cx = self.getCoon()
		cu = cx.execute("SELECT * FROM OVSTABLE WHERE HOSTNAME ='"+host_name+"';")
		rows = cu.fetchall()
		cx.close()
		return rows	
		
	def selectOvsWithBrname(self,br_name):
		cx = self.getCoon()
		cu = cx.execute("SELECT * FROM OVSTABLE WHERE BRNAME ='"+br_name+"';")
		rows = cu.fetchall()
		cx.close()
		return rows	
	
	def selectContainerWithBr(self,br_name):
		cx = self.getCoon()
		cu = cx.execute("SELECT CONTAINERID FROM CONTAINERTABLE WHERE BRNAME ='"+br_name+"';")
		rows = cu.fetchall()
		cx.close()
		return rows	
		
	def selectContainerWithBrname(self,br_name,container_id):
		cx = self.getCoon()
		cu = cx.execute("SELECT * FROM CONTAINERTABLE WHERE BRNAME ='"+br_name+"' AND CONTAINERID ='"+container_id+"';")
		rows = cu.fetchall()
		cx.close()
		return rows
		
	def selectContainerWithServicename(self,service_name):
		cx = self.getCoon()
		cu = cx.execute("SELECT * FROM CONTAINERTABLE WHERE SERVICENAME ='"+service_name+"';")
		rows = cu.fetchall()
		cx.close()
		return rows	
		
	def selectContainerWithContainerid(self,container_id):
		cx = self.getCoon()
		cu = cx.execute("SELECT * FROM CONTAINERTABLE WHERE CONTAINERID ='"+container_id+"';")
		rows = cu.fetchall()
		cx.close()
		return rows	
		
	def addOvs(self,vtepname,username,hostname,vtepip):
		cx = self.getCoon()
		cu=cx.cursor()
		v = (vtepname,username,hostname,vtepip)
		ins = "INSERT INTO OVSTABLE(BRNAME,USERNAME,HOSTNAME,VTEPIP) VALUES (?,?,?,?);"
		cu.execute(ins,v)
		cx.commit()
		cx.close()
		
	def addContainer(self,container_id,br_name,port_name,user_name,service_name,container_ip):
		try:
			cx = self.getCoon()
			cu=cx.cursor()
			v = (container_id,br_name,port_name,user_name,service_name,container_ip)
			ins = "INSERT INTO CONTAINERTABLE(CONTAINERID,BRNAME,PORTNAME,USERNAME,SERVICENAME,CONTAINERIP) VALUES (?,?,?,?,?,?);"
			cu.execute(ins,v)
			cx.commit()
			cx.close()
		except:
			return 'error'
		else:
			return 'success'		
	def delOvsWithBrname(self,br_name):
		try:
			cx = self.getCoon()
			'''cu=cx.cursor()
			v = (br_name)
			ins = "DELETE FROM OVSTABLE WHERE BRNAME = ?;"
			cu.execute(ins,v)'''
			cx.execute("DELETE FROM OVSTABLE WHERE BRNAME = '"+br_name+"';")
			cx.commit()
			cx.close()
		except:
			return 'error'
		else:
			return 'success'
		
	def delContainerWithPortname(self,port_name):
		try:
			cx = self.getCoon()
			cx.execute("DELETE FROM CONTAINERTABLE WHERE PORTNAME ='"+port_name+"';")
			cx.commit()
			cx.close()
		except:
			return 'error'
		else:
			return 'success'
		
	def setTable(self):
		self.coon.execute('CREATE TABLE OVSTABLE \
		(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
		BRNAME TEXT NOT NULL,\
		USERNAME TEXT,\
		HOSTNAME TEXT NOT NULL,\
		VTEPIP TEXT NOT NULL);')
		
		self.coon.execute('CREATE TABLE CONTAINERTABLE \
		(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
		CONTAINERID TEXT NOT NULL, \
		BRNAME TEXT NOT NULL,\
		PORTNAME TEXT NOT NULL,\
		USERNAME TEXT,\
		SERVICENAME TEXT,\
		CONTAINERIP TEXT NOT NULL);')
		self.coon.close()
