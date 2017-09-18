import os
import time
from sqliteagent import Sqlite_Agent
import randomkey

class Network_agent():
	def __init__(self,file_dir):
		self.file_dir = file_dir
		self.sqlconn = Sqlite_Agent()
	
	'''
	ovs_bridge_create(user_name,host_name,vtep_ip,host_ips)
	���Դ���ovs���š�
	
	������
	user_name�������û�����
	host_name����Ҫ����������
	vtep_ip����Ҫ����������ovs ���ŵ�ip�����Ρ�
	host_ips���б����Ա�ʶovs����vxlan������ͨ�ŵ�remote_ip��remote_ip���ú�������ͬһovs�����ϵ��������Կ�����ͨ�ţ��ɴ����б�
	
	����ֵ��
	�½���ovs�������ƣ��ַ������ͣ������쳣���򷵻ء�error����ͷ���쳣�ı�����������������Ĭ��Ϊveth+������
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
			interface_name = "veth"+randomkey.key_gen()
			os.popen('sudo ovs-vsctl add-port '+br_name+' '+interface_name+' -- set interface '+interface_name+' type=vxlan options:remote_ip='+ip)
			time.sleep(0.2)
			
		return ovs_network.br_name


	'''
	add_ovs_bridge_remoteip(br_name,host_ips)
	ΪOVS���ſ�����vxlanͨ������remote_ip
	
	������
	br_name��ovs��������
	host_ips���б��ɿգ����Ա�ʶovs����vxlan������ͨ�ŵ�remote_ip��remote_ip���ú�������ͬһovs�����ϵ��������Կ�����ͨ��
	
	�޷���ֵ
	'''
	def add_ovs_bridge_remoteip(self,br_name,host_ips):
		for ip in host_ips:
			print(ip)
			interface_name = "veth"+randomkey.key_gen()
			os.popen('sudo ovs-vsctl add-port '+br_name+' '+interface_name+' -- set interface '+interface_name+' type=vxlan options:remote_ip='+ip)
			time.sleep(0.2)
			
	'''
	container_network_create(br_name,container_id,user_name,network_name,container_ip,tag_id)
	��������ovs����������
	
	������
	br_name�����ӵ�ovs�������ƣ�ͬһbr_name�ϵ��������Ի���ͨ��
	container_id������id
	user_name��Ԥ���������û���
	network_name��Ԥ����������������������������
	container_ip����Ҫ�������������������ip�����Ρ�
	tag_id���Ǳ�Ҫ������vlan���룬Ҳ���Ǹ������,������Ҫ���ø��룬����-1
	
	����ֵ������ip���ַ������ͣ������쳣���򷵻ء�error����ͷ���쳣�ı�
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
	
		port_name = 'eth'+randomkey.key_gen()
		
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
	�������� id��ȡ���ݿ��д洢����ovs���Ű󶨵�����������
	
	������
	container_id������id
	
	����ֵ�������������ƣ��ַ������ͣ������쳣���򷵻ء�error����ͷ���쳣�ı�
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
	������������ovs���ŵ�vlan�������
	
	������
	br_name�����ӵ�ovs�������ƣ�ͬһbr_name�ϵ��������Ի���ͨ��
	port_name�������˿�
	container_id������id
	tag_id������vlan���룬Ҳ���Ǹ������
	
	����ֵ������id���ַ������ͣ������쳣���򷵻ء�error����ͷ���쳣�ı�
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
	����ovs��������ɾ��ovs���š�
	
	������
	br_name�����ӵ�ovs�������ƣ����ݴ����ƽ���ovs���ŵ�ɾ��
	
	����ֵ��
	�ɹ����ء�success����ʧ�ܷ��ء�error����ͷ�쳣�ַ���
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
	����������ɾ��ovs���š�
	
	������
	network_name������������������
	
	����ֵ��
	�ɹ����ء�success����ʧ�ܷ��ء�error����ͷ�쳣�ַ���
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
	����������������������idɾ�����������ڼ����Ŷ˿ڣ���������ovs���Ž�󣬵�������ɾ��������
	
	������
	br_name��ovs������
	port_name�������˿���
	container_id������id
	
	����ֵ��
	�ɹ����ء�success����ʧ�ܷ��ء�error����ͷ�쳣�ַ���
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
	��������idɾ�����������ڼ����Ŷ˿ڣ�ʹ������ovs���Ž��
	������
	br_name��ovs������
	container_id������id
	����ֵ��
	�ɹ����ء�success����ʧ�ܷ��ء�error����ͷ�쳣�ַ���
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
	����������ɾ����ǰ�����´�������������������ڼ����Ŷ˿ڣ���������ovs���Ž��
	������
	br_name��ovs������
	network_name������������������
	
	����ֵ��
	�ɹ����ء�success����ʧ�ܷ��ء�error����ͷ�쳣�ַ���
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
	������������ѯ�������Ƿ���ovs���š�
	
	������
	host_name��������
	
	����ֵ��
	�ɹ����������������������򷵻ؿ��ַ�����ʧ�ܷ��ء�error����ͷ�쳣�ַ���
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
	��������ӵ�������������swarm overlay�����С�
	
	������
	network_name��������
	
	����ֵ��
	����������
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
	���docker0���Ŷ���Ӧ���������Ρ�
	
	������
	host_ips����Ҫ������ε�����ip
	
	����ֵ��
	��
	'''
	def container_remove_drop_host(self,host_ips):
		for ip in host_ips:
			print('container_remove_drop_host ip : '+ip)
			os.popen('sudo iptables -D DOCKER -s '+ip+' -j DROP')
			time.sleep(0.1)	
	
	'''
	network_nat(network_card,s_port,d_ip_port)
	����ָ��������nat��
	
	������
	network_card����ǰ����ָ������
	s_port����ǰ����ת��Դ�˿�
	d_ip_port��Ŀ���������˿�
	
	����ֵ��
	��
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
	

		
	

