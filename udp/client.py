import pyaudio
import numpy as np
import socket
import select

#The following code comes from markjay4k as referenced below

chunk=256
RATE=16000
timeout=0.01

p=pyaudio.PyAudio()

#output stream setup
player=p.open(format = pyaudio.paInt16,rate=RATE,channels=1, output=True, frames_per_buffer=chunk)


client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
client.bind(("", 37020))
print ("Your IP address is: ", socket.gethostbyname(socket.gethostname()))
client.setblocking(0)

#print("Start")


while True:            #Used to continuously stream audio
    try:
        ready = select.select([client], [], [], timeout) # check if any data in socket
        print(ready[0])
        if (ready[0]):
            rcvdata, addr = client.recvfrom(256 * 2)
            player.write(rcvdata)
    except socket.timeout:
        pass
    
#closes streams
stream.stop_stream()
stream.close()
p.terminate