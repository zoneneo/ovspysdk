import sqlite3
from sqlitemanager import Sqlite_Manager
import objtojson
import os
import time

class Network_manager():
	def __init__(self):
		self.sqlconn = Sqlite_Manager()
		
	'''
	add_network(network_type,user_name,service_name,network_name)
	���Դ���������Ϣ���洢�����ݿ��С�
	������
	network_type���������ͣ���Ϊ��swarm�� �� ��ovs��
	user_name�������û���
	service_name������������Ҫͨ���û����ͷ�����ȷ��Ψһ��������
	network_name������������
	
	����ֵ��
	�ɹ��������������ַ������ͣ������쳣���򷵻ء�error����ͷ���쳣�ַ���
	'''	
	def add_network(self,network_type,user_name,service_name,network_name):
		sqlconn = self.sqlconn
		try:
			ovs = sqlconn.selectNetworkWithName(network_name)
		except:
			print('add_network selectNetworkname database error')
			return 'error:1-database error'
		else:
			if len(ovs)>0:
				print('add_network network_name is using')
				return 'error:2-network name is using'
		
		if network_type == 'swarm':
			os.popen('sudo docker network create -d=overlay '+network_name)
		
		try:
			sqlconn.addNetwork(network_type,user_name,service_name,network_name)
		except:
			print('add_network addNetwork database error')
			return 'error:1-database error'
			
		return network_name
	
	
	'''
	del_network(network_type,network_name)
	����ɾ�����ݿ���������Ϣ��
	������
	network_type���������ͣ���Ϊ��swarm�� �� ��ovs��
	network_name������������
	
	����ֵ��
	�ɹ����ء�success�����ַ������ͣ�ʧ�ܷ��ء�error���������쳣���򷵻ء�error����ͷ���쳣�ı�
	'''	
	def del_network(self,network_type,network_name):
		sqlconn = self.sqlconn
		result = 'error'
		try:
			result = sqlconn.delNetwork(network_type,network_name)
		except:
			print('del_network delNetwork database error')
			return 'error:1-database error'
			
		if network_type == 'swarm':
			os.popen('sudo docker network rm '+network_name)
			
		time.sleep(0.5)
		
		return result	
	
	'''
	add_swarm_network(user_name,service_name,network_name)
	���Դ���swarm������Ϣ���洢�����ݿ��С�
	������
	user_name�������û���
	service_name������������Ҫͨ���û����ͷ�����ȷ��Ψһ��������
	network_name������������
	
	����ֵ��
	�ɹ��������������ַ������ͣ������쳣���򷵻ء�error����ͷ���쳣�ı�
	'''
	def add_swarm_network(self,user_name,service_name,network_name):
		sqlconn = self.sqlconn
		try:
			ovs = sqlconn.selectNetworkWithName(network_name)
		except:
			print('add_swarm_network selectNetworkname database error')
			return 'error:1-database error'
		else:
			if len(ovs)>0:
				print('add_swarm_network network name is using')
				return 'error:2-network name is using'
		
		os.popen('sudo docker network create -d=overlay '+network_name)
		
		try:
			sqlconn.addNetwork('swarm',user_name,service_name,network_name)
		except:
			print('add_swarm_network addNetwork database error')
			return 'error:1-database error'

		#time.sleep(0.5)
		return network_name
			
	'''
	del_swarm_network(network_name)
	����ɾ�����ݿ���swarm������Ϣ��
	������
	network_name������������
	
	����ֵ��
	�ɹ����ء�success�����ַ������ͣ�ʧ�ܷ��ء�error���������쳣���򷵻ء�error����ͷ���쳣�ı�
	'''		
	def del_swarm_network(self,network_name):
		sqlconn = self.sqlconn
		result = 'error'
		try:
			result = sqlconn.delNetwork('swarm',network_name)
			os.popen('sudo docker network rm '+network_name)
			time.sleep(0.5)
		except:
			print('del_swarm_network delNetwork database error')
			return 'error:1-database error'
			
		return result
		
	
	'''
	add_ovs_network(user_name,service_name,network_name)
	���Դ���ovs������Ϣ���洢�����ݿ��С�
	������
	user_name�������û���
	service_name������������Ҫͨ���û����ͷ�����ȷ��Ψһ��������
	network_name������������
	
	����ֵ��
	�ɹ��������������ַ������ͣ������쳣���򷵻ء�error����ͷ���쳣�ı�
	'''
	def add_ovs_network(self,user_name,service_name,network_name):
		sqlconn = self.sqlconn
		try:
			rows = sqlconn.selectNetworkWithName(network_name)
		except:
			print('add_ovs_network selectNetworkname database error')
			return 'error:1-database error'
		else:
			if len(rows)>0:
				print('add_ovs_network network name is using')
				return 'error:2-network name is using'
		
		try:
			sqlconn.addNetwork('ovs',user_name,service_name,network_name)
		except:
			print('swarm_network_create addOvsNetwork database error')
			return 'error:1-database error'
			
		return network_name
	
	'''
	del_ovs_network(network_name)
	����ɾ�����ݿ���ovs������Ϣ��
	������
	network_name������������
	
	����ֵ��
	�ɹ����ء�success�����ַ������ͣ�ʧ�ܷ��ء�error���������쳣���򷵻ء�error����ͷ���쳣�ı�
	'''
	def del_ovs_network(self,network_name):
		sqlconn = self.sqlconn
		result = 'error'
		try:
			self.del_host_with_network(network_name)
			result = sqlconn.delNetwork('ovs',network_name)
		except:
			print('del_swarm_network delNetwork database error')
			return 'error:1-database error'
		return result	
	
	'''
	get_network(network_type,user_name,service_name)
	��ȡ���ݿ�����������
	������
	network_type���������ͣ���Ϊ��swarm�� �� ��ovs��
	user_name�������û���
	service_name������������Ҫͨ���û����ͷ�����ȷ��Ψһ��������
	
	����ֵ��
	�ɹ��������������ַ������ͣ������쳣���򷵻ء�error����ͷ���쳣�ı�
	'''	
	def get_network(self,network_type,user_name,service_name):
		sqlconn = self.sqlconn
		network_name = ''
		try:
			rows = sqlconn.selectNetworkWithUserService(network_type,user_name,service_name)
		except:
			print('get_network getOvsNetwork database error')
			return 'error:1-database error'
		else:
			if len(rows) == 0:
				print('get_network network not found')
				return 'error:3-network not found'
		
		for row in rows:
			network_name = row[4]
			
		return network_name
	
	
	'''
	add_host_ovs_network(host_ip,network_name)
	�������ovs������ͨ��������Ϣ���洢�����ݿ��С�
	������
	host_ip������ip
	network_name������������
	
	����ֵ��
	�ɹ����ء�success�����ַ������ͣ������쳣���򷵻ء�error����ͷ���쳣�ı�	
	'''
	def add_host_ovs_network(self,host_ip,network_name):
		sqlconn = self.sqlconn
		rows = sqlconn.getNetworkWithNetworkName(network_name)
		if len(rows)==0:
			print('add_host_ovs_network network not found')
			return 'error:3-network not found'
		rows = sqlconn.getHost(host_ip,network_name)
		if len(rows)>0:
			print('add_host_ovs_network host in the network')
			return 'error:4-host in the network'
		try:
			sqlconn.addHostOvsNetwork(network_name,host_ip)
		except:
			print('add_host_ovs_network addHostOvsNetwork database error')
			return 'error:1-database error'
			
		return 'success'
	
	'''
	get_host(host_ip,network_name)
	�����������Լ�������ip�ж�������ip�Ƿ������Ӧ�����С�
	������
	network_name������������
	
	����ֵ��
	����ip�б����У����б���>0�����ޣ����б���=0	
		'''	
	def get_host(self,host_ip,network_name):
		sqlconn = self.sqlconn
		rows = []
		try:
			rows = sqlconn.getHost(host_ip,network_name)
		except:
			print('get_host delHostOvsNetwork database error')
			return 'error:1-database error'
			
		return rows
		
	'''
	get_host_ovs_network(network_name)
	������������ȡovs����������ͨ����������ip��
	������
	network_name������������
	
	����ֵ��
	�ɹ�����ip�б������쳣���򷵻ء�error����ͷ���쳣�ı�	
	'''	
	def get_host_ovs_network(self,network_name):
		sqlconn = self.sqlconn
		ovsNetworkHosts = []
		try:
			rows = sqlconn.getHostOvsNetwork(network_name)
		except:
			print('get_host_ovs_network getHostOvsNetwork database error')
			return 'error:1-database error'
		
		for row in rows:
			ovsNetworkHosts.append(row[2])
			
		return ovsNetworkHosts
	
	
	'''
	del_host_with_hostip(host_ip,network_name)
	����������ip��������ɾ����Ӧ��������Ϣ��
	������
	host_ip������ip
	network_name������������
	
	����ֵ��
	�ɹ����ء�success����ʧ�ܷ��ء�error���������쳣���򷵻ء�error����ͷ���쳣�ı�
	'''
	def del_host_with_hostip(self,host_ip,network_name):
		sqlconn = self.sqlconn
		result = 'error'
		try:
			result = sqlconn.delHostWithHostip(host_ip,network_name)
		except:
			print('del_host_with_hostip delHostWithHostip database error')
			return 'error:1-database error'
		
		return result
	
	'''
	del_host_with_nework(network_name)
	����������ɾ����Ӧ��������Ϣ��
	������
	network_name������������
	
	����ֵ��
	�ɹ����ء�success����ʧ�ܷ��ء�error���������쳣���򷵻ء�error����ͷ���쳣�ı�	
		'''	
	def del_host_with_network(self,network_name):
		sqlconn = self.sqlconn
		result = 'error'
		try:
			result = sqlconn.delHostWithNetwork(network_name)
		except:
			print('del_host_with_network delHostWithNetwork database error')
			return 'error:1-database error'
		
		return result
		
		
class OvsNetworkHost():
	def __init__(self,ovsname,hostip):
		self.ovs_name = ovsname
		self.host_ip = hostip
	
