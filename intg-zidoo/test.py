import asyncio
import json
import socket

import netifaces
from ssdp import aio, messages, network
import socket

from zidooaio import ZidooRC

class MyProtocol(aio.SimpleServiceDiscoveryProtocol):

    def response_received(self, response, addr):
        print(response, addr)

    def request_received(self, request, addr):
        print(request, addr)


# loop = asyncio.get_event_loop()
# connect = loop.create_datagram_endpoint(MyProtocol, family=socket.AF_INET)
# transport, protocol = loop.run_until_complete(connect)
#
# notify = messages.SSDPRequest('NOTIFY')
# notify.sendto(transport, (network.MULTICAST_ADDRESS_IPV4, network.PORT))
#
# try:
#     loop.run_forever()
# except KeyboardInterrupt:
#     pass
#
# transport.close()
# loop.close()

# toto = [i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None)]
# print(*toto, sep=",")
#
# ips = []
# for interface in netifaces.interfaces():
#     addresses = netifaces.ifaddresses(interface)
#     for address in addresses.get(netifaces.AF_INET, []):
#         ips.append(address["addr"])
# print(*toto, sep=",")
loop=asyncio.new_event_loop()
device = ZidooRC("192.168.1.40", loop=loop)
data = asyncio.run(device.connect())
asyncio.run(device.disconnect())
print(json.dumps(data))
