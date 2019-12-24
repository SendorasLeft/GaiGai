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
RCV_MULTIPLIER = 2 # 2 works well on mac, 4 works better on pi
RATE = 16000 # to be adjusted according to available soundcard
TIMEOUT = 0.01 # receiver select-check timeout
TTL = struct.pack('b', 1) # udp datagram time-to-live

MULTICAST_IP = '224.3.29.71'
SERVER_PORT = 10000

RADIO_MIC_PORTS = [10100, 10101, 10102]
CLIENT_PORTS = [10200, 10201, 10202]
CHANNEL_PREF_PORTS = [10300, 10301, 10302]

# -1 denotes disconnected radio
radio_channels = {-1:{radio_idx for radio_idx in range(len(RADIO_MIC_PORTS))}
                     ,0:set()
                     ,1:set()
                     ,2:set()}
channel_prefs = np.array([-1, -1, -1])

# radio
server_multicast_group = (MULTICAST_IP, SERVER_PORT)

# receiver
multicast_group = MULTICAST_IP
server_address = ('', 10000)

not_shutdown = True

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
        print("Subscription Update: Subscribed to socket multicast IP", socket.gethostbyname(socket.gethostname()), "on port", port)
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

def update_radio_membership(radio_idx, channel):
    if channel_prefs[radio_idx] == channel:
        return
    elif not (channel in radio_channels):
        return
    else:
        radio_channels[channel_prefs[radio_idx]].discard(radio_idx)
        radio_channels[channel].add(radio_idx)
        channel_prefs[radio_idx] = channel


# receiver thread that averages signal from all the subscribed sockets
# TODO: set mode so that user can toggle between listening to all ports or to a specific port
def receiver_thread(subscribed_sockets, server_socket, timeout, chunk_size, rcv_multiplier, channel=0):
    global not_shutdown, channel_prefs, radio_channels
    while not_shutdown: # need to set flag for poweron/off

        rcvdata_map = {}
        for radio_idx in range(len(subscribed_sockets)):
            rcvdata_map[radio_idx] = None

        ready = select.select(subscribed_sockets, [], [], timeout) # check if any data present in subscribed sockets
        radio_idx = 0
        #all_received_data = []
        for client in subscribed_sockets:
            try:
                if (ready[radio_idx] and channel_prefs[radio_idx] != -1): # if socket has data
                    rcvdata, addr = client.recvfrom(chunk_size * rcv_multiplier)
                    decoded_data = np.fromstring(rcvdata, dtype=np.int16)
                    print(decoded_data)
                    rcvdata_map[radio_idx] = decoded_data
                    #all_received_data.append(decoded_data)
            except socket.timeout:
                pass
            radio_idx += 1

        server_response(server_socket, channel_prefs, radio_channels, rcvdata_map, CLIENT_PORTS)

        # if at least one subscribed socket is actively sending data, average the signal and play to speakers
        # if (len(all_received_data) > 0):
        #     if (channel == 0): # channel 0 is for broadcasting sounds from all radios
        #         averaged_signal = sum(all_received_data) // len(all_received_data)
        #         player.write(averaged_signal.tostring())

def compose_radiostream(rcvdata_map, channel_pref, radio_idx, radio_channels):
    radiostream_data_list = []
    for member in radio_channels[channel_pref]:
        if rcvdata_map[member] is not None: #and  member != radio_idx:
            radiostream_data_list.append(rcvdata_map[member])
    if (len(radiostream_data_list) > 0):
        return sum(radiostream_data_list) // len(radiostream_data_list)
    else:
        return None



def server_response(server_socket, channel_prefs, radio_channels, rcvdata_map, client_ports):
    for radio_idx in range(len(channel_prefs)):
        if channel_prefs[radio_idx] != -1:
            send_data = compose_radiostream(rcvdata_map=rcvdata_map
                                            ,channel_pref=channel_prefs[radio_idx]
                                            ,radio_idx=radio_idx
                                            ,radio_channels=radio_channels)
            if send_data is not None:
                server_socket.sendto(send_data.tostring(), (MULTICAST_IP, CLIENT_PORTS[radio_idx]))


def channel_pref_thread(subscribed_sockets, timeout=1):
    global not_shutdown, channel_prefs
    while not_shutdown:
        ready = select.select(subscribed_sockets, [], [], timeout)

        radio_idx = 0
        for client in subscribed_sockets:
            try:
                if (ready[radio_idx]):
                    rcvdata, _ = client.recvfrom(1)
                    update_radio_membership(radio_idx, int(rcvdata.decode()))
            except socket.timeout:
                if channel_prefs[radio_idx] != -1:
                    print("Radio", radio_idx, "has disconnected.")
                    update_radio_membership(radio_idx, -1)
            #TODO: add exception clause for typecast exception
            radio_idx += 1

# driver function
def main():
    server_socket = server_multicast_setup(ttl=TTL, timeout=TIMEOUT)
    channelprefs_sockets = subscription_multicast_setup(multicast_group=MULTICAST_IP, subscription_ports=CHANNEL_PREF_PORTS)
    radio_mic_sockets = subscription_multicast_setup(multicast_group=MULTICAST_IP, subscription_ports=RADIO_MIC_PORTS)

    channel_prefs_receiving_thread = Thread(target=channel_pref_thread
                                                ,args=(channelprefs_sockets,))

    receiving_thread = Thread(target=receiver_thread
                                ,args=(radio_mic_sockets, server_socket, TIMEOUT, CHUNK, RCV_MULTIPLIER,))

    # nested function for handling signal interrupts. closes streams and sockets, then exits all threads gracefully
    def SIGINT_handler(*args):
        global not_shutdown
        print(" Handling signal interrupt...")
        not_shutdown = False
        channel_prefs_receiving_thread.join()
        receiving_thread.join()

        server_socket.close()
        for client in radio_mic_sockets:
            client.close()
        for client in channelprefs_sockets:
            client.close()

        sys.exit()


    signal.signal(signal.SIGINT, SIGINT_handler)
    # sending_thread.start()
    channel_prefs_receiving_thread.start()
    receiving_thread.start()

    # don't let main thread die
    while True:
        signal.pause()


if __name__ == "__main__":
    main()
