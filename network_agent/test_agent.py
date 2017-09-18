from agent import Network_agent

import unittest
HOST,USER,ADRR,VTEP_IP,CONTAINER='ubuntu','s','','',''
class WidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.agt = Network_agent('/home/ubuntu')
        self.adaptor='veth'.USER       

    def test_ovs_bridge_create(self):
        self.agt.ovs_bridge_create(HOST,USER,VTEP_IP,[])
    def test_add_ovs_bridge_remoteip(self):
        self.agt.add_ovs_bridge_remoteip(self.adaptor,[ADRR])
    def test_add_ovs_bridge_remoteip(self):
        self.agt.add_ovs_bridge_remoteip(self.adaptor,[ADRR])
    def test_container_network_create(self):
        self.agt.container_network_create(self.adaptor,CONTAINER,'s','serv1',VTEP_IP+'1',1)
        agt.add_ovs_bridge_remoteip(self.adaptor,[ADRR])

if __name__ == '__main__':
    if len(sys.argv) == 3:
        ADRR,CONTAINER=sys.argv[1],sys.argv[3]
        VTEP_IP='192.168.1.'+sys.argv[2]
        unittest.main()
        sys.exit(0)
    else:
        print "usage: %s 11.1.97.227 1 f8f4255d7867" % sys.argv[0]
        sys.exit(2)

    