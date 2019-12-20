import pyaudio
import numpy as np
import socket

#The following code comes from markjay4k as referenced below

chunk=256
RATE=16000

p=pyaudio.PyAudio()

#input stream setup
stream=p.open(format = pyaudio.paInt16,rate=RATE,channels=1, input_device_index = 2, input=True, frames_per_buffer=chunk)

#the code below is from the pyAudio library documentation referenced below
#output stream setup
#player=p.open(format = pyaudio.paInt16,rate=RATE,channels=1, output=True, frames_per_buffer=chunk)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.settimeout(0.1)

while True:            #Used to continuously stream audio
    data=np.fromstring(stream.read(chunk,exception_on_overflow = False),dtype=np.int16)
    server.sendto(data, ('<broadcast>', 37020))
    
#closes streams
stream.stop_stream()
stream.close()
p.terminate