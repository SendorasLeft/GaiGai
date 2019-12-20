import pyaudio
import numpy as np
import socket

#The following code comes from markjay4k as referenced below

chunk = 512
RATE= 16000
port = 5001

p=pyaudio.PyAudio()

#input stream setup
stream=p.open(format = pyaudio.paInt16,rate=RATE,channels=1, input_device_index = 2, input=True, frames_per_buffer=chunk)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create the socket
server_socket.bind(('', port)) # listen on port 5000
server_socket.listen(5) # queue max 5 connections
print("Your IP address is: ", socket.gethostbyname(socket.gethostname()))
print("Server Waiting for client on port ", port)
client_socket, address = server_socket.accept()


while True:            #Used to continuously stream audio
    data=np.fromstring(stream.read(chunk,exception_on_overflow = False),dtype=np.int16)
    try:
       client_socket.sendall(data)
    except e:
       print(e)

#closes streams
stream.stop_stream()
stream.close()
p.terminate
