from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class DynamicFirewall(object):
    def __init__ (self, connection):
        self.connection = connection
        connection.addListeners(self)
        self.mac_to_port = {}
        self.packet_counts = {} 
        log.info("Firewall activated on switch %s", connection)

    def _handle_PacketIn (self, event):
        packet = event.parsed
        if not packet.parsed: return

        if packet.type == 0x88cc or packet.type == 0x86dd:
            return

        # --- DYNAMIC BLOCKING LOGIC ---
        src_mac = str(packet.src)
        self.packet_counts[src_mac] = self.packet_counts.get(src_mac, 0) + 1

        if self.packet_counts[src_mac] > 5:
            log.warning("SUSPICIOUS ACTIVITY from %s! Installing DROP rule.", src_mac)
            
            # Install hardware DROP rule
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match(dl_src=packet.src)
            msg.idle_timeout = 60 # Block for 60 seconds
            msg.priority = 100 # High priority to override anything else
            self.connection.send(msg)
            return
        # ------------------------------

        # Normal Forwarding (Using PacketOut so the switch doesn't cache the flow)
        self.mac_to_port[packet.src] = event.port
        if packet.dst in self.mac_to_port:
            out_port = self.mac_to_port[packet.dst]
        else:
            out_port = of.OFPP_FLOOD

        msg = of.ofp_packet_out()
        msg.actions.append(of.ofp_action_output(port = out_port))
        msg.data = event.ofp
        msg.in_port = event.port
        self.connection.send(msg)

def launch ():
    def start_switch (event):
        DynamicFirewall(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
