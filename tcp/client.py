import pyaudio
import numpy as np
import socket

#The following code comes from markjay4k as referenced below

chunk = 512
RATE = 16000
port = 5001

p=pyaudio.PyAudio()

ip = "127.0.0.1"

#the code below is from the pyAudio library documentation referenced below
#output stream setup
player=p.open(format = pyaudio.paInt16,rate=RATE,channels=1, output=True, frames_per_buffer=chunk)

#Create a socket connection for connecting to the server:
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip, port))

while True:            #Used to continuously stream audio
    data = client_socket.recv(1024)
    player.write(data,chunk)
    
#closes streams
#stream.stop_stream()
#stream.close()
p.terminate
