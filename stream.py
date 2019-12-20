import pyaudio
import numpy as np
import sys
import socket

chunk = 4096
RATE = 16000
rcv_port = 5000
channels = 1

def create_audio_IO_streams():
    p=pyaudio.PyAudio()

    #input stream from mic
    stream=p.open(format = pyaudio.paInt16,rate=RATE,channels=channels, input_device_index = 2, input=True, frames_per_buffer=chunk)

    #the code below is from the pyAudio library documentation
    player=p.open(format = pyaudio.paInt16,rate=RATE,channels=channels, output=True, frames_per_buffer=chunk)


# logistics setup for streaming
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', port)) # listen on port 5000
server_socket.listen(5) # queue max 5 connections
client_socket, address = server_socket.accept()
print("Your IP address is: ", socket.gethostbyname(socket.gethostname()))
print(address)
print("Server Waiting for client on port ", port)

# logistics setup for receiving
ip = "192.168.43.94"
#rcv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rcv_socket.connect((ip, port))

p, stream, player = create_audio_IO_streams()

while True:            #Used to continuously stream audio
    # send audio
    try:
        client_socket.sendall(stream.read(chunk))
    except e:
        print("Error in sending stream chunk")
        print(e)

    # receive audio
    data = rcv_socket.recv(1024)
    stream.write(data,chunk)

    data=np.fromstring(stream.read(chunk,exception_on_overflow = False),dtype=np.int16)
    player.write(data,chunk)
    
#closes streams
stream.stop_stream()
stream.close()
socket.close()
p.terminate