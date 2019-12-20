import pyaudio
import numpy as np
import socket
import select
import threading
from threading import Thread


chunk = 512
RCV_MULTIPLIER = 2
RATE = 16000
timeout = 0.01
#IP = '127.0.0.1'
ip = 'localhost'

p=pyaudio.PyAudio()
stream=p.open(format = pyaudio.paInt16,rate=RATE,channels=1, input_device_index = 2, input=True, frames_per_buffer=chunk)
player=p.open(format = pyaudio.paInt16,rate=RATE,channels=1, output=True, frames_per_buffer=chunk)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.settimeout(0.1)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
client.bind(("", 37020))
print ("Your IP address is: ", socket.gethostbyname(socket.gethostname()))
client.setblocking(0)

def receiver_thread():
    while True:            #Used to continuously stream audio
        print("hello")
        try:
            ready = select.select([client], [], [], timeout) # check if any data in socket
            if (ready[0]):
                rcvdata, addr = client.recvfrom(chunk * RCV_MULTIPLIER)
                player.write(rcvdata)
        except socket.timeout:
            pass

def broadcaster_thread():
    while True:            #Used to continuously stream audio
        data=np.fromstring(stream.read(chunk,exception_on_overflow = False),dtype=np.int16)
        server.sendto(data, ('localhost', 37020))

sending_thread = Thread(target=broadcaster_thread) #args=(arg,)
receiving_thread = Thread(target=receiver_thread) #args=(arg,)

sending_thread.start()
receiving_thread.start()





