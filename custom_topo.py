from mininet.topo import Topo

class ProjectTopo(Topo):
    def build(self):
        # Add a single switch
        s1 = self.addSwitch('s1')

        # Add 3 hosts with specific IPs
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')

        # Add links between the hosts and the switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

# This dictionary allows Mininet to find our topology via the command line
topos = {'project_topo': (lambda: ProjectTopo())}
