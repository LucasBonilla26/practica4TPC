from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt

log = core.getLogger()

class Tutorial (object):
  """
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

    # Use this table to keep track of which ethernet address is on
    # which switch port (keys are MACs, values are ports).
    self.mac_to_port = {}
    self.buffer = []

    self.switch_interfaces = {'10.0.1.1':['00:00:00:00:00:11',1],
                         '10.0.2.1':['00:00:00:00:00:22',2],
                         '10.0.3.1':['00:00:00:00:00:33',3]}

    self.ip_to_mac = {}

  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port=out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)


  def act_like_hub (self, packet, packet_in):
    """
    Implement hub-like behavior -- send all packets to all ports besides
    the input port.
    """

    # We want to output to all ports -- we do that using the special
    # OFPP_ALL port as the output port.  (We could have also used
    # OFPP_FLOOD.)
    self.resend_packet(packet_in, of.OFPP_ALL)

    # Note that if we didn't get a valid buffer_id, a slightly better
    # implementation would check that we got the full data before
    # sending it (len(packet_in.data) should be == packet_in.total_len)).


  def act_like_switch (self, packet, packet_in):
    """
    Implement switch-like behavior.
    """
    # DELETE THIS LINE TO START WORKING ON THIS (AND THE ONE BELOW!) #

    # Here's some psuedocode to start you off implementing a learning
    # switch.  You'll need to rewrite it as real Python code.

    # Learn the port for the source MAC
    sourceAddr = str(packet.src)
    destinationAddr = str(packet.dst)
    inputPort = packet_in.in_port
    self.mac_to_port[sourceAddr] = inputPort

    if destinationAddr in self.mac_to_port:
      # Send packet out the associated port
      outputPort = self.mac_to_port[destinationAddr]
      self.resend_packet(packet_in, outputPort)

      # Once you have the above working, try pushing a flow entry
      # instead of resending the packet (comment out the above and
      # uncomment and complete the below.)

      log.debug("Installing flow...")
      # Maybe the log statement should have source/destination/port?

      msg = of.ofp_flow_mod()
      #
      ## Set fields to match received packet
      #msg.match = of.ofp_match.from_packet(packet)
      my_match = of.ofp_match()
      my_match.dl_dst = packet.dst
      msg.match = my_match
      msg.idle_timeout = 10
      action = of.ofp_action_output(port = outputPort)
      msg.actions.append(action)
      self.connection.send(msg)
      #
      #< Set other fields of flow_mod (timeouts? buffer_id?) >
      #
      #< Add an output action, and send -- similar to resend_packet() >

    else:
      # Flood the packet out everything but the input port
      # This part looks familiar, right?
      self.resend_packet(packet_in, of.OFPP_ALL)



  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """    
    packet = event.parsed # This is the parsed packet data.
    packet_in = event.ofp # The actual ofp_packet_in message.

    print(packet)

    if packet.type == packet.ARP_TYPE or packet.type == packet.IP_TYPE:
      
      sourceAddr = str(packet.src)
      destinationAddr = str(packet.dst)
      inputPort = packet_in.in_port
      self.mac_to_port[sourceAddr] = inputPort

      print(self.mac_to_port)
      print(self.ip_to_mac)
      
      if packet.type == packet.ARP_TYPE:
        
        self.ip_to_mac[str(packet.payload.protosrc)]=str(packet.src)
        
        if str(packet.payload.protodst) in self.switch_interfaces.keys() and packet.payload.opcode == pkt.arp.REQUEST:
          #ARP REQUEST A INTERFAZ DEL SWITCH DEVUELVE ARP REPLY
          arp_reply = pkt.arp()
          arp_reply.hwsrc = pkt.EthAddr(self.switch_interfaces[str(packet.payload.protodst)][0]) #funciona
          arp_reply.hwdst = packet.src
          arp_reply.opcode = pkt.arp.REPLY
          arp_reply.protosrc = packet.payload.protodst
          arp_reply.protodst = packet.payload.protosrc

          ether = pkt.ethernet()
          ether.type = pkt.ethernet.ARP_TYPE
          ether.dst = packet.src
          ether.src = pkt.EthAddr(self.switch_interfaces[str(packet.payload.protodst)][0]) #funciona
          ether.payload = arp_reply

          self.resend_packet(ether, out_port=self.switch_interfaces[str(packet.payload.protodst)][1])
      
      elif packet.type == packet.IP_TYPE:
        #CONOZCO LA MAC DE DESTINO DEL PAQUETE IP
        self.ip_to_mac[str(packet.payload.srcip)]=str(packet.src)

        #PING TO A SWITCH INTERFACE
        if str(packet.payload.dstip) in self.switch_interfaces.keys():
          print("LLEGA IP AL SWITCH")
          seq = packet.payload.payload.payload.seq #ip-icmp-echo.seq
          id = packet.payload.payload.payload.id

          icmp = pkt.icmp()
          icmp.type = pkt.TYPE_ECHO_REPLY #ECHO REPLY
          icmp.code = pkt.TYPE_ECHO_REPLY
          icmp.payload = packet.payload.payload.payload

          ip = pkt.ipv4()
          ip.protocol = packet.payload.protocol
          ip.srcip = packet.payload.dstip
          ip.dstip = packet.payload.srcip
          #ip.id = packet.payload.id
          ip.payload = icmp

          ether = pkt.ethernet()
          ether.type = pkt.ethernet.IP_TYPE
          ether.payload = ip
          ether.src = packet.dst
          ether.dst = packet.src

          print(ether.src)
          print(ether.dst)
          print(ip.srcip)
          print(ip.dstip)

          print(self.switch_interfaces[str(packet.payload.dstip)][1])
          self.resend_packet(ether, out_port=self.switch_interfaces[str(packet.payload.dstip)][1])

        elif str(packet.payload.dstip) in self.ip_to_mac.keys() and self.ip_to_mac[str(packet.payload.dstip)] in self.mac_to_port:
          ether = pkt.ethernet()
          ether.type = pkt.ethernet.IP_TYPE
          ether.payload = packet.payload
          ether.src = packet.dst
          ether.dst = pkt.EthAddr(self.ip_to_mac[str(packet.payload.dstip)])
          print(ether)
          self.resend_packet(ether, out_port=self.mac_to_port[self.ip_to_mac[str(packet.payload.dstip)]])
        
        else:
          #NO CONOZCO LA MAC, SWITCH MANDA ARP REQUEST BROADCAST
          arp_request = pkt.arp()
          arp_request.hwsrc = packet.dst
          arp_request.hwdst = pkt.EthAddr.BROADCAST
          arp_request.opcode = pkt.arp.REQUEST
          arp_request.protosrc = packet.payload.srcip
          arp_request.protodst = packet.payload.dstip
          print(arp_request)
          ether = pkt.ethernet()
          ether.type = pkt.ethernet.ARP_TYPE
          ether.dst = pkt.EthAddr.BROADCAST
          ether.src = packet.dst
          ether.payload = arp_request
          print(ether)
          self.resend_packet(ether, of.OFPP_ALL)


def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Tutorial(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
