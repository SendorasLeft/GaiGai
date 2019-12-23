import pyaudio
import numpy as np
import socket
import select
import threading
from threading import Thread
import struct
import signal
import sys

# general UDP segment parameters
CHUNK = 256
RCV_MULTIPLIER = 4 # 2 works well on mac, 4 works better on pi
RATE = 16000 # to be adjusted according to available soundcard
TIMEOUT = 0.01 # receiver select-check timeout
TTL = struct.pack('b', 1) # udp datagram time-to-live

MULTICAST_IP = '224.3.29.71'
SERVER_PORT = 10000

RECEIVER_PORTS = [10000] # list of multicast subscriptions

# sender
server_multicast_group = (MULTICAST_IP, SERVER_PORT)

# receiver
multicast_group = MULTICAST_IP
server_address = ('', 10000)

not_shutdown = True

# initializes pyaudio reference, stream from microphone, player stream to speaker
def IO_setup(rate, frames_per_buffer, channels=1, type_format=pyaudio.paInt16):
    p = pyaudio.PyAudio()
    stream = p.open(format=type_format,rate=rate,channels=channels, input_device_index=2, input=True, frames_per_buffer=frames_per_buffer)
    player = p.open(format=type_format,rate=rate,channels=channels, output=True, frames_per_buffer=frames_per_buffer)
    return p, stream, player

# initializes single multicast server port for streaming all mic sounds
def server_multicast_setup(ttl, timeout):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    server.settimeout(0.1)
    return server

# given a multicast IP and a list of subscription ports,
# return a list of initialized multicast listener sockets
def subscription_multicast_setup(multicast_group, subscription_ports):
    subscribed_sockets = []

    for port in subscription_ports:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        client.bind(('', port))
        group = socket.inet_aton(multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        client.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        print ("Subscription Update: Subscribed to socket multicast IP ", socket.gethostbyname(socket.gethostname()), "on port", port)
        client.setblocking(0)
        subscribed_sockets.append(client)

    return subscribed_sockets

# server thread that continually publishes mic audio using the server socket
def server_thread(server_socket, stream, chunk_size, server_multicast_group):
    global not_shutdown
    while not_shutdown: # need to set flag for poweron/poweroff
        data = np.fromstring(stream.read(chunk_size ,exception_on_overflow = False), dtype=np.int16)
        #print(data)
        server_socket.sendto(data.tostring(), server_multicast_group)

# receiver thread that averages signal from all the subscribed sockets
# TODO: set mode so that user can toggle between listening to all ports or to a specific port
def receiver_thread(subscribed_sockets, player, timeout, chunk_size, rcv_multiplier, channel=0):
    global not_shutdown
    while not_shutdown: # need to set flag for poweron/off
        ready = select.select(subscribed_sockets, [], [], timeout) # check if any data present in subscribed sockets

        idx = 0
        all_received_data = []
        for client in subscribed_sockets:
            try:
                if (ready[idx]): # if socket has data
                    rcvdata, addr = client.recvfrom(chunk_size * rcv_multiplier)
                    all_received_data.append(np.fromstring(rcvdata, dtype=np.int16))
            except socket.timeout:
                pass
            idx += 1

        # if at least one subscribed socket is actively sending data, average the signal and play to speakers
        if (len(all_received_data) > 0):
            if (channel == 0): # channel 0 is for broadcasting sounds from all radios
                averaged_signal = sum(all_received_data) // len(all_received_data)
                player.write(averaged_signal.tostring())

# driver function
def main():
    p, stream, player = IO_setup(rate=RATE, frames_per_buffer=CHUNK)
    server_socket = server_multicast_setup(ttl=TTL, timeout=TIMEOUT)
    subscribed_sockets = subscription_multicast_setup(multicast_group=MULTICAST_IP, subscription_ports=RECEIVER_PORTS)

    sending_thread = Thread(target=server_thread
                                ,args=(server_socket, stream, CHUNK, server_multicast_group,))

    receiving_thread = Thread(target=receiver_thread
                                ,args=(subscribed_sockets, player, TIMEOUT, CHUNK, RCV_MULTIPLIER,))

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
        for client in subscribed_sockets:
            client.close()

        sys.exit()


    signal.signal(signal.SIGINT, SIGINT_handler)
    sending_thread.start()
    receiving_thread.start()

    # don't let main thread die
    while True:
        signal.pause()


if __name__ == "__main__":
    main()




