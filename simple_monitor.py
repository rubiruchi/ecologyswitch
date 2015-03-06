from operator import attrgetter

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

#import urllib
#import urllib2
import requests
import json
import ast

class SimpleMonitor(simple_switch_13.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.rx_bytes = [0,0]
        self.tx_bytes = [0,0]
        self.utilization= [0.0,0.0]
        self.ports = [1,1]
        self.monitoring_time = 5;
        self.macsOfSwitch={}

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        self.getMacsOfSwitch()
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(self.monitoring_time)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)


    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            if (stat.port_no == 1):
                self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d', 
                                 ev.msg.datapath.id, stat.port_no,
                                 stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                                 stat.tx_packets, stat.tx_bytes, stat.tx_errors)
                
                deltatraffic= (stat.rx_bytes - self.rx_bytes[stat.port_no-1]) + (stat.tx_bytes - self.tx_bytes[stat.port_no-1])
                self.logger.info('\nDelta traffic port 1: %f \n', deltatraffic )
                self.logger.info('\n delta rx: %d \n', stat.rx_bytes - self.rx_bytes[stat.port_no-1] )
                self.logger.info('\n delta tx: %f \n', stat.tx_bytes - self.tx_bytes[stat.port_no-1] )
                self.utilization[stat.port_no - 1] = deltatraffic * 8 * 100 / (self.monitoring_time * 1*1000000.0) 
                self.logger.info('\nutilization port 1: %f', self.utilization[stat.port_no-1] )
                self.tx_bytes [stat.port_no - 1] = stat.tx_bytes
                self.rx_bytes [stat.port_no - 1] = stat.rx_bytes
                


                self.logger.info("\nrerouting\n")
                self.reroute(self.mac_to_port)

                '''
                if ( (port2 is down) and port1_util > 70 ) :
                    #enable port2
                    self._modify_port(2,0)
                    self.ports[1]=1
                    self.reroute()
                else if ( (port2 is up) and port1_util + port2_util < 90) :
                    self.reroute()
                    #disable port2
                    self._modify_port(2,8)
                    self.ports[1]=0
                '''


    def _modify_port(self,port_no,config):
        url = 'http://localhost:8080/stats/portdesc/modify'
        payload = {
          'dpid': 1,
          'port_no': port_no,
          'config': config,
          'mask' : 0
        }
        response = requests.post(url,data=payload)
        self.logger.info(response.text)
        

    def getMacsOfSwitch(self):
        url = 'http://localhost:8080/stats/portdesc/1'
        response = requests.get(url)
        temp2={}
        if (response.text):
            portdescarrays = ast.literal_eval(response.text)["1"]
            for temp in portdescarrays:
                temp2[temp['port_no']] = temp['hw_addr']
            self.macsOfSwitch = temp2

    def reroute(self,mac_to_port):
        self.logger.info(mac_to_port)
        hit = 0
        mac_h1 = ""
        for mac, port in mac_to_port[1].items():
            if port == 1 and not(mac in self.macsOfSwitch.values()) :
                mac_h1 = mac
                self.logger.info(mac_h1)
                
                break


        #if port1 and port2 is active:
            #modify the flows
            #set so that traffic from odd ports come to port 1, and from even ports come to port 2
        url = 'http://localhost:8080/stats/flowentry/modify'
        port_output =  1
        for i in range(1,5):

            if i % 2 == 0:
                port_output = 2
            else:
                port_output = 1

            payload = {
              "dpid": 1,
              "match":{
                     "dl_dst": mac_h1,
                     "in_port": i
                },
              "actions":[
                    {
                        "type":"OUTPUT",
                        "port": port_output

                    }
              ]
            }
            
            response = requests.post(url,data=json.dumps(payload))
            self.logger.info(response.text)

