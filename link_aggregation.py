from mininet.cli import CLI
from mininet.link import Link
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.term import makeTerm
from mininet.node import UserSwitch
from mininet.link import TCLink

if '__main__' == __name__:
    net = Mininet(controller=RemoteController)

    c0 = net.addController('c0',ip="127.0.0.1")

    s1 = net.addSwitch('s1',cls=UserSwitch)

    h1 = net.addHost('h1')
    h2 = net.addHost('h2', mac='00:00:00:00:00:22')
    h3 = net.addHost('h3', mac='00:00:00:00:00:23')
    h4 = net.addHost('h4', mac='00:00:00:00:00:24')

    TCLink(s1, h1, bw=1)
    TCLink(s1, h1, bw=1)
    TCLink(s1, h2, bw=1)
    TCLink(s1, h3, bw=1)
    TCLink(s1, h4, bw=1)

    net.build()
    c0.start()
    s1.start([c0])

    

    CLI(net)

    net.stop()