import pyaudio
import numpy as np
import socket
import select
import threading
from threading import Thread
import struct

# general UDP segment parameters
chunk = 256
RCV_MULTIPLIER = 4 # 2 works well on mac, 4 works better on pi
RATE = 16000 # to be adjusted according to available soundcard
timeout = 0.01

# sender
server_multicast_group = ('224.3.29.71', 10000)

# receiver
multicast_group = '224.3.29.71'
server_address = ('', 10000)
ttl = struct.pack('b', 1)

p=pyaudio.PyAudio()
stream=p.open(format = pyaudio.paInt16,rate=RATE,channels=1, input_device_index = 2, input=True, frames_per_buffer=chunk)
player=p.open(format = pyaudio.paInt16,rate=RATE,channels=1, output=True, frames_per_buffer=chunk)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# Enable broadcasting mode
#server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
server.settimeout(0.1)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
#client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
client.bind(server_address)
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
client.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
print ("Your IP address is: ", socket.gethostbyname(socket.gethostname()))
client.setblocking(0)

def receiver_thread():
    while True: # need to set flag for poweron/off
        try:
            ready = select.select([client], [], [], timeout) # check if any data in socket
            if (ready[0]):
                rcvdata, addr = client.recvfrom(chunk * RCV_MULTIPLIER)
                player.write(rcvdata)
        except socket.timeout:
            pass

def broadcaster_thread():
    while True: # need to set flag for poweron/poweroff
        data=np.fromstring(stream.read(chunk,exception_on_overflow = False),dtype=np.int16)
        server.sendto(data, server_multicast_group)

sending_thread = Thread(target=broadcaster_thread) #args=(arg,)
receiving_thread = Thread(target=receiver_thread) #args=(arg,)

sending_thread.start()
receiving_thread.start()





