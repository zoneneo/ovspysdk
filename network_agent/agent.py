import os
import time
from sqliteagent import Sqlite_Agent

import string
import random

def key_gen(length):
	b_str='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
	keylist = [random.choice(b_str) for i in range(length)]
	return "" .join(keylist)

class Network_agent():
	def __init__(self,file_dir):
		self.file_dir = file_dir
		self.sqlconn = Sqlite_Agent()
	
	'''
	ovs_bridge_create(user_name,host_name,vtep_ip,host_ips)
	用以创建ovs网桥。
	
	参数：
	user_name：用作用户名。
	host_name：必要，主机名。
	vtep_ip：必要，用以设置ovs 网桥的ip及网段。
	host_ips：列表，用以标识ovs网络vxlan跨主机通信的remote_ip。remote_ip设置后，连接在同一ovs网桥上的容器可以跨主机通信，可传空列表。
	
	返回值：
	新建的ovs网桥名称，字符串类型，若有异常，则返回“error”开头的异常文本。创建的网桥名称默认为veth+主机名
	'''	
	def ovs_bridge_create(self,user_name,host_name,vtep_ip,host_ips):
		print("user_name : "+user_name+" ; host_name : "+host_name+" ; vtep_ip : "+vtep_ip)
		sqlconn = self.sqlconn
		try:
			ovs = self.sqlconn.selectOvsWithHostname(host_name)
		except:
			print('ovs_bridge_create selectOvsWithHostname database error')
			return 'error:1-database error'
		else:
			if len(ovs)>0:
				print('ovs_bridge_create bridge is using')
				return 'error:2-bridge is using'
		
		br_name = "veth"+host_name
		
		os.popen('sudo ovs-vsctl add-br '+br_name)
		time.sleep(0.4)
		os.popen('sudo ifconfig '+br_name+' '+vtep_ip)
		ovs_network = Ovs_network(user_name,host_name,vtep_ip,br_name)
		
		try:
			sqlconn.addOvs(br_name,user_name,host_name,vtep_ip)
		except:
			print('ovs_bridge_create addOvs database error')
			return 'error:1-database error'
		
		for ip in host_ips:
			interface_name = "veth"+key_gen(12)
			os.popen('sudo ovs-vsctl add-port '+br_name+' '+interface_name+' -- set interface '+interface_name+' type=vxlan options:remote_ip='+ip)
			time.sleep(0.2)
			
		return ovs_network.br_name


	'''
	add_ovs_bridge_remoteip(br_name,host_ips)
	为OVS网桥跨主机vxlan通信设置remote_ip
	
	参数：
	br_name：ovs网桥名称
	host_ips：列表，可空，用以标识ovs网络vxlan跨主机通信的remote_ip。remote_ip设置后，连接在同一ovs网桥上的容器可以跨主机通信
	
	无返回值
	'''
	def add_ovs_bridge_remoteip(self,br_name,host_ips):
		for ip in host_ips:
			print(ip)
			interface_name = "veth"+key_gen(12)
			os.popen('sudo ovs-vsctl add-port '+br_name+' '+interface_name+' -- set interface '+interface_name+' type=vxlan options:remote_ip='+ip)
			time.sleep(0.2)
			
	'''
	container_network_create(br_name,container_id,user_name,network_name,container_ip,tag_id)
	创建基于ovs的容器网络
	
	参数：
	br_name：连接的ovs网桥名称，同一br_name上的容器可以互相通信
	container_id：容器id
	user_name：预留，用作用户名
	network_name：预留，用作服务名（或者网络名）
	container_ip：必要，用以设置容器网络的ip及网段。
	tag_id：非必要，可做vlan隔离，也就是隔离机制,若不需要配置隔离，则传输-1
	
	返回值：容器ip，字符串类型，若有异常，则返回“error”开头的异常文本
	'''	
	def container_network_create(self,br_name,container_id,user_name,network_name,container_ip,tag_id):
	
		sqlconn = self.sqlconn
		try:
			container = sqlconn.selectContainerWithBrname(br_name,container_id)
		except:
			print('container_network_create selectContainerWithBrname database error')
			return 'error:1-database error'
		else:
			if len(container)>0:
				print('have container in br_name with container_id : '+container_id)
				return 'error:3-container is connect bridge'
			else:
				print('container is free')
	
		port_name = 'eth'+key_gen(12)
		
		container_network = Container_network(br_name,port_name,container_id,container_ip)
		os.popen('ovs-docker add-port '+br_name+' '+port_name+' '+container_id)
		time.sleep(0.1)
		os.popen('sudo docker exec -it '+container_id+' ifconfig '+port_name+' '+container_ip)
		if(tag_id >= 0):
			os.popen('ovs-docker set-vlan '+br_name+' '+port_name+' '+container_id+' '+tag_id)
		print('docker port is create')
		
		try:
			sqlconn.addContainer(container_id,br_name,port_name,user_name,network_name,container_ip)
		except:
			print('container_network_create addContainer database error')
			return 'error:1-database error'
			
		return container_network.container_ip
		
	'''
	container_get_portname(container_id)
	根据容器 id获取数据库中存储的与ovs网桥绑定的容器内网口
	
	参数：
	container_id：容器id
	
	返回值：容器网口名称，字符串类型，若有异常，则返回“error”开头的异常文本
	'''	
	def container_get_portname(self,container_id):
		result = 'error'
		sqlconn = self.sqlconn
		try:
			container = sqlconn.selectContainerWithContainerid(container_id)
		except:
			print('container_get_portname selectContainerWithContainerid database error')
			return 'error:1-database error'
			
		for row in rows:
			port_name = row[3]
			print('container_get_portname port_name : '+port_name)
			result = port_name
			
		return result
		
	
		
	'''
	set_container_tag(br_name,port_name,container_id,tag_id)
	配置容器基于ovs网桥的vlan隔离策略
	
	参数：
	br_name：连接的ovs网桥名称，同一br_name上的容器可以互相通信
	port_name：容器端口
	container_id：容器id
	tag_id：可做vlan隔离，也就是隔离机制
	
	返回值：容器id，字符串类型，若有异常，则返回“error”开头的异常文本
	'''
	def set_container_tag(self,br_name,port_name,container_id,tag_id):
		try:
			container = sqlconn.selectContainerWithBrname(br_name,container_id)
		except:
			print('set_container_tag selectContainerWithBrname database error')
			return 'error:1-database error'
		else:
			if len(container)<1:
				print('set_container_tag:no container_id : '+container_id)
				return 'error:4-container is not connect bridge'
			else:
				print('container is connect bridge')
			
		os.popen('ovs-docker set-vlan '+br_name+' '+port_name+' '+container_id+' '+tag_id)
		print('ovs container tag is done')
		return container_id
		
	'''
	del_ovs_bridge_brname(br_name)
	根据ovs网桥名称删除ovs网桥。
	
	参数：
	br_name：连接的ovs网桥名称，根据此名称进行ovs网桥的删除
	
	返回值：
	成功返回“success”，失败返回“error”开头异常字符串
	'''	
	def del_ovs_bridge_brname(self,br_name):
		sqlconn = self.sqlconn
		try:
			result = sqlconn.delOvsWithBrname(br_name)
		except:
			print('del_ovs_bridge_brname delOvsWithBrname database error')
			return 'error:1-database error'
		
		if result == 'success':
			os.popen('sudo ovs-vsctl del-br '+br_name)
				
		try:
			rows = sqlconn.selectContainerWithBr(br_name)
		except:
			print('del_ovs_bridge_brname selectContainerWithBr database error')
			return 'error:1-database error'
		
		for row in rows:
			container_id = row[0]
			self.del_container_network_portname(br_name,container_id)
		
		return result	
		
	'''
	del_ovs_bridge_hostname(host_name)
	根据主机名删除ovs网桥。
	
	参数：
	network_name：服务名（网络名）
	
	返回值：
	成功返回“success”，失败返回“error”开头异常字符串
	'''	
	def del_ovs_bridge_hostname(self,host_name):
		result = 'error:5-bridge is not found'
		sqlconn = self.sqlconn
		try:
			rows = sqlconn.selectOvsWithHostname(host_name)
		except:
			print('del_ovs_bridge_hostname selectOvsWithHostname database error')
			return 'error:1-database error'
		
		for row in rows:
			br_name = row[1]
			print('del_ovs_bridge_hostname br_name : '+br_name)
			result = self.del_ovs_network_brname(br_name)
			
		return result
		
	'''
	del_container_network_pn_cd(port_name,container_id)
	根据容器内网口名及容器id删除容器内网口及网桥端口，既容器与ovs网桥解绑，但并不是删除容器。
	
	参数：
	br_name：ovs网桥名
	port_name：容器端口名
	container_id：容器id
	
	返回值：
	成功返回“success”，失败返回“error”开头异常字符串
	'''	
	def del_container_network_pn_ci(self,br_name,port_name,container_id):
		sqlconn = self.sqlconn
		try:
			result = sqlconn.delContainerWithPortname(port_name,container_id)
			print('del_container_network_portname result is '+result)
		except:
			print('del_container_network_portname delContainerWithPortname database error')
			return 'error:1-database error'
		
		if result == 'success':
			os.popen('sudo ovs-docker del-port '+br_name+' '+port_name+' '+container_id)
			
		return result
	
	
	'''
	del_container_network_containerid(container_id)
	根据容器id删除容器内网口及网桥端口，使容器与ovs网桥解绑。
	参数：
	br_name：ovs网桥名
	container_id：容器id
	返回值：
	成功返回“success”，失败返回“error”开头异常字符串
	'''	
	def del_container_network_containerid(self,br_name,container_id):
		result = 'error'
		sqlconn = self.sqlconn
		try:
			rows = sqlconn.selectContainerWithContainerid(container_id)
		except:
			print('del_container_network_containerid selectContainerWithContainerid database error')
			return 'error:1-database error'
		
		for row in rows:
			port_name = row[3]
			print('del_container_network_containerid   port_name : '+port_name)
			result = self.del_container_network_pn_ci(br_name,port_name,container_id)
			
		return result
		
	'''
	del_container_network_nn(network_name)
	根据网络名删除当前主机下此网络的所有容器内网口及网桥端口，既容器与ovs网桥解绑
	参数：
	br_name：ovs网桥名
	network_name：服务名（网络名）
	
	返回值：
	成功返回“success”，失败返回“error”开头异常字符串
	'''	
	def del_container_network_nn(self,br_name,network_name):
		result = 'error'
		sqlconn = self.sqlconn
		try:
			rows = sqlconn.selectContainerWithServicename(network_name)
		except:
			print('del_container_network_sn_ci selectContainerWithServicename database error')
			return 'error:1-database error'
			
		for row in rows:
			port_name = row[3]
			container_id = row[6]
			print('del_container_network_containerid   port_name : '+port_name+' ; container_id :'+container_id)
			result = self.del_container_network_pn_ci(br_name,port_name,container_id)
			
		return result
		
		
	'''
	get_ovs_brname_hostname(host_name)
	根据主机名查询主机内是否建立ovs网桥。
	
	参数：
	host_name：主机名
	
	返回值：
	成功返回网桥名，若无网桥则返回空字符串，失败返回“error”开头异常字符串
	'''	
	def get_ovs_brname_hostname(self,host_name):
		br_name = ''
		sqlconn = self.sqlconn
		try:
			rows = sqlconn.selectOvsWithHostname(host_name)
		except:
			print('get_ovs_brname_hostname selectOvsWithHostname database error')
			return 'error:1-database error'
		
		for row in rows:
			br_name = row[1]
			print('get_ovs_brname_hostname br_name : '+br_name)
		
		return br_name
		
		
	'''
	container_swarmnetwork_connect(container_id,network_name)
	将容器添加到具体网络名的swarm overlay网络中。
	
	参数：
	network_name：网络名
	
	返回值：
	返回网络名
	'''	
	def container_swarmnetwork_connect(self,container_id,network_name):
		os.popen('sudo docker network connect '+network_name+' '+container_id)
		time.sleep(0.5)
			
		return network_name
		
	
	def container_swarmnetwork_disconnect(self,container_id,network_name):
		os.popen('sudo docker network disconnect '+network_name+' '+container_id)
		time.sleep(0.5)
			
		return network_name	

 
	def container_drop_host(self,host_ips):
		for ip in host_ips:
			print('container_drop_host ip : '+ip)
			os.popen('sudo iptables -I DOCKER -s '+ip+' -j DROP')
			time.sleep(0.1)
			
	'''
	container_remove_drop_host(host_ips)
	解除docker0网桥对相应主机的屏蔽。
	
	参数：
	host_ips：需要解除屏蔽的主机ip
	
	返回值：
	无
	'''
	def container_remove_drop_host(self,host_ips):
		for ip in host_ips:
			print('container_remove_drop_host ip : '+ip)
			os.popen('sudo iptables -D DOCKER -s '+ip+' -j DROP')
			time.sleep(0.1)	
	
	'''
	network_nat(network_card,s_port,d_ip_port)
	设置指定网卡的nat。
	
	参数：
	network_card：当前主机指定网卡
	s_port：当前主机转发源端口
	d_ip_port：目的主机及端口
	
	返回值：
	无
	'''		
	def network_nat(self,network_card,s_port,d_ip_port):
		os.popen('iptables -t nat -A PREROUTING -p tcp -i '+network_card+' --dport '+s_port+' -j DNAT --to '+d_ip_port)
		os.popen('iptables -t nat -A POSTROUTING -j MASQUERADE')
	
	
			
class Ovs_network():
	def __init__(self,user_name,host_name,vtep_ip,br_name):
		self.user_name = user_name
		self.host_name = host_name
		self.vtep_ip = vtep_ip
		self.br_name = br_name

class Container_network():
	def __init__(self,br_name,port_name,container_id,container_ip):
		self.br_name = br_name
		self.port_name = port_name
		self.container_id = container_id
		self.container_ip = container_ip
	

		
	

