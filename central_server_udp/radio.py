import pyaudio
import numpy as np
import socket
import select
import threading
from threading import Thread
import struct
import signal
import sys
import time

# general UDP segment parameters
CHUNK = 256
RCV_MULTIPLIER = 2 # 2 works well on mac, 4 works better on pi
RATE = 16000 # to be adjusted according to available soundcard
TIMEOUT = 0.01 # receiver select-check timeout
TTL = struct.pack('b', 1) # udp datagram time-to-live

#PREFS_TTL = struct.pack('b', 0.3)

MULTICAST_IP = '224.3.29.71'
SENDER_PORT = 10100
RECEIVER_PORT = 10200
CHANNEL_PREF_PORT = 10300

channel_preference = 0

# sender
server_multicast_group = (MULTICAST_IP, SENDER_PORT)
channel_multicast_group = (MULTICAST_IP, CHANNEL_PREF_PORT)

# receiver
multicast_group = MULTICAST_IP

not_shutdown = True

# initializes pyaudio reference, stream from microphone, player stream to speaker
def IO_setup(rate, frames_per_buffer, channels=1, type_format=pyaudio.paInt16):
    p = pyaudio.PyAudio()
    stream = p.open(format=type_format,rate=rate,channels=channels, input_device_index=2, input=True, frames_per_buffer=frames_per_buffer)
    player = p.open(format=type_format,rate=rate,channels=channels, output_device_index=1, output=True, frames_per_buffer=frames_per_buffer)
    return p, stream, player

# initializes single multicast server port for streaming all mic sounds
def server_multicast_setup(ttl, timeout):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    server.settimeout(0.1)
    return server

def channel_preference_setup(ttl, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    sock.settimeout(0.1)
    return sock

# given a multicast IP and a list of subscription ports,
# return a list of initialized multicast listener sockets
def subscription_multicast_setup(multicast_group, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
    client.bind(('', port))
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    client.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print ("Subscription Update: Subscribed to socket multicast IP ", socket.gethostbyname(socket.gethostname()), "on port", port)
    client.setblocking(0)

    return client

# server thread that continually publishes mic audio using the server socket
def server_thread(server_socket, stream, chunk_size, server_multicast_group):
    global not_shutdown
    while not_shutdown: # need to set flag for poweron/poweroff
        data = np.fromstring(stream.read(chunk_size ,exception_on_overflow = False), dtype=np.int16)
        #print(data)
        server_socket.sendto(data.tostring(), server_multicast_group)

# receiver thread that averages signal from all the subscribed sockets
# TODO: set mode so that user can toggle between listening to all ports or to a specific port
def receiver_thread(receiver_socket, player, timeout, chunk_size, rcv_multiplier):
    global not_shutdown
    while not_shutdown: # need to set flag for poweron/off
        ready, _, _ = select.select([receiver_socket], [], [], timeout) # check if any data present in subscribed sockets
        try:
            if (receiver_socket in ready): # if socket has data
                rcvdata, addr = receiver_socket.recvfrom(chunk_size * rcv_multiplier)
                #print(rcvdata)
                player.write(rcvdata)
        except socket.timeout:
            pass

def channel_preference_thread(channel_socket, channel_multicast_group):
    global channel_preference, not_shutdown
    while not_shutdown:
        data = str(channel_preference)
        channel_socket.sendto(data.encode(), channel_multicast_group)
        time.sleep(0.1)

# driver function
def main():
    p, stream, player = IO_setup(rate=RATE, frames_per_buffer=CHUNK)
    server_socket = server_multicast_setup(ttl=TTL, timeout=TIMEOUT)
    receiver_socket = subscription_multicast_setup(multicast_group=MULTICAST_IP, port=RECEIVER_PORT)
    channel_socket = channel_preference_setup(ttl=TTL, timeout=TIMEOUT)

    sending_thread = Thread(target=server_thread
                                ,args=(server_socket, stream, CHUNK, server_multicast_group,))

    receiving_thread = Thread(target=receiver_thread
                                ,args=(receiver_socket, player, TIMEOUT, CHUNK, RCV_MULTIPLIER,))

    channelpref_thread = Thread(target=channel_preference_thread
                                    ,args=(channel_socket, channel_multicast_group,))

    # nested function for handling signal interrupts. closes streams and sockets, then exits all threads gracefully
    def SIGINT_handler(*args):
        global not_shutdown
        print("handling signal interrupt...")
        not_shutdown = False
        sending_thread.join()
        receiving_thread.join()

        stream.stop_stream()
        stream.close()
        player.stop_stream()
        player.close()
        p.terminate()

        server_socket.close()
        receiver_socket.close()
        channel_socket.close()

        sys.exit()


    signal.signal(signal.SIGINT, SIGINT_handler)
    sending_thread.start()
    receiving_thread.start()
    channelpref_thread.start()

    # don't let main thread die
    while True:
        signal.pause()


if __name__ == "__main__":
    main()




