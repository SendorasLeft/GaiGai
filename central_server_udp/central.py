import pyaudio
import numpy as np
import socket
import select
from threading import Thread
import struct
import signal
import sys
import time

# general UDP segment parameters
CHUNK = 64
RCV_MULTIPLIER = 1  # 2 works well on mac, 4 works better on pi
RATE = 16000  # to be adjusted according to available sound-card
TIMEOUT = 0.01  # receiver select-check timeout
TTL = struct.pack('b', 1)  # udp datagram time-to-live

MULTICAST_IP = '224.3.29.71'
SERVER_PORT = 10000

RADIO_MIC_PORTS = [10100, 10101, 10102, 10103]
CLIENT_PORTS = [10200, 10201, 10202, 10203]
CHANNEL_PREF_PORTS = [10300, 10301, 10302, 10303]

# the -1 channel denotes disconnected radios
radio_channels = {-1: {radio_idx for radio_idx in range(len(RADIO_MIC_PORTS))}
    , 0: set()
    , 1: set()
    , 2: set()}
channel_prefs = np.array([-1, -1, -1, -1, -1, -1])

# radio
server_multicast_group = (MULTICAST_IP, SERVER_PORT)

# receiver
multicast_group = MULTICAST_IP
server_address = ('', 10000)

not_shutdown = True


def server_multicast_setup(ttl, timeout=0.1):
    """Returns a server socket (UDP multicast).

    :param ttl: struct denoting number of "network layers" before datagram expires
    :param timeout: socket timeout in seconds
    :return: server socket
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    server.settimeout(timeout)
    return server


def subscription_multicast_setup(multicast_ip, subscription_ports):
    """Returns a list of UDP multicast sockets initialized based on a single IP and multiple subscription ports.

    :param multicast_ip: multicast IP address as string
    :param subscription_ports: list of port numbers as integers
    :return: list of non-blocking multicast sockets corresponding to the supplied IP and ports
    """
    subscribed_sockets = []

    for port in subscription_ports:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        client.bind(('', port))
        group = socket.inet_aton(multicast_ip)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        client.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print("Subscription Update: Subscribed to socket multicast IP"
              , socket.gethostbyname(socket.gethostname())
              , "on port"
              , port)

        client.setblocking(0)
        subscribed_sockets.append(client)

    return subscribed_sockets


def update_radio_membership(radio_idx, channel):
    """Updates the current channel membership of the radio with ID radio_idx to the supplied channel.

    :param radio_idx: integer ID of the radio
    :param channel: channel to switch the radio to. -1 denotes disconnection.
    """
    global radio_channels, channel_prefs
    if channel_prefs[radio_idx] == channel:
        return
    elif not (channel in radio_channels):
        return
    else:
        radio_channels[channel_prefs[radio_idx]].discard(radio_idx)
        radio_channels[channel].add(radio_idx)
        if channel != -1 and channel_prefs[radio_idx] == -1:
            print("[CONNECT] Update: Radio"
                  , radio_idx
                  , "is now connected to the central server on channel"
                  , channel)
        elif channel == -1 and channel_prefs[radio_idx] != -1:
            print("[DISCONNECT] Update: Radio", radio_idx, "has disconnected.")
        elif channel_prefs[radio_idx] != channel:
            print(
            "[CHANNEL CHANGE] Update: Radio", radio_idx, "has switched from channel", channel_prefs[radio_idx], "to",
            channel)
        channel_prefs[radio_idx] = channel


def receiver_thread(subscribed_sockets, server_socket, timeout, chunk_size, rcv_multiplier):
    """Main server thread that continually receives incoming microphone data from all client radio ports, then
    responds back with the correct stream depending on their channel membership.

    :param subscribed_sockets: list of sockets to receive microphone data from
    :param server_socket: server socket used to send response
    :param timeout: time-out for select checking on all subscribed_sockets for received data
    :param chunk_size: bytes of data to receive
    :param rcv_multiplier: multiplier for chunk_size. when this is 1, then bytes received is equal to chunk_size
    """
    global not_shutdown, channel_prefs, radio_channels
    while not_shutdown:  # need to set flag for poweron/off

        rcvdata_map = {}
        for radio_idx in range(len(subscribed_sockets)):
            rcvdata_map[radio_idx] = None

        ready_sockets, _, _ = select.select(subscribed_sockets, [], [], timeout)  # check if sockets are ready to read
        radio_idx = 0
        for client in subscribed_sockets:
            try:
                if (client in ready_sockets) and (channel_prefs[radio_idx] != -1):  # if socket has data
                    rcvdata, addr = client.recvfrom(chunk_size * rcv_multiplier)
                    decoded_data = np.fromstring(rcvdata, dtype=np.int16)
                    # print(decoded_data)
                    rcvdata_map[radio_idx] = decoded_data
            except socket.timeout:
                pass
            radio_idx += 1

        # respond to the connected radios
        server_response(server_socket, channel_prefs, radio_channels, rcvdata_map, CLIENT_PORTS)


def server_response(server_socket, channel_prefs, radio_channels, rcvdata_map, client_ports):
    """Streams back the appropriate audio response to all connected radios based on their channel memberships.

    :param server_socket: server socket used to send response
    :param channel_prefs: 1D numpy array or list denoting channel memberships of all radios. -1 denotes disconnection.
    :param radio_channels: dict mapping each channel number to a set containing all radios in the channel
    :param rcvdata_map: dict mapping all radio_idx to the mic data received. None denotes no data from the radio.
    :param client_ports:
    :return:
    """
    for radio_idx in range(len(channel_prefs)):
        if channel_prefs[radio_idx] != -1:
            send_data = compose_radiostream(rcvdata_map=rcvdata_map
                                            , channel_pref=channel_prefs[radio_idx]
                                            , radio_idx=radio_idx
                                            , radio_channels=radio_channels)
            if send_data is not None:
                server_socket.sendto(send_data.tostring(), (MULTICAST_IP, client_ports[radio_idx]))


def compose_radiostream(rcvdata_map, channel_pref, radio_idx, radio_channels):
    """Composes the data response to be sent back to a specific radio. Performs audio averaging for all members in
    the channel that the radio belongs to.

    :param rcvdata_map: dict mapping all radio_idx to the mic data received. None denotes no data from the radio.
    :param channel_pref: 1D numpy array or list denoting channel memberships of all radios. -1 denotes disconnection.
    :param radio_idx: Integer ID of the radio.
    :param radio_channels: dict mapping each channel number to a set containing all radios in the channel.
    :return: 1D numpy array denoting the audio response to be sent back to the radio.
    """
    radiostream_data_list = []
    for member in radio_channels[channel_pref]:
        if rcvdata_map[member] is not None:  # and  member != radio_idx: # TODO: add this back for production
            radiostream_data_list.append(rcvdata_map[member])
    if len(radiostream_data_list) > 0:
        return sum(radiostream_data_list) // len(radiostream_data_list)
    else:
        return None


def channel_pref_thread(subscribed_sockets, timeout=0.3, sleep=0.3):
    """Receives channel membership preference from all radios, then switches their membership accordingly. This
    thread is also responsible for updating connection status based on UDP packet inactivity (ie. when a radio
    fails to send their channel preference within a time period defined by timeout and sleep. Channel preference data
    is currently received as a single character string literal, corresponding to a single integer.

    :param subscribed_sockets: list of radio sockets to receive channel preferences from.
    :param timeout: socket timeout in seconds (float).
    :param sleep: seconds (float) to sleep before checking for radio channel preferences again.
    :return:
    """
    global not_shutdown, channel_prefs
    while not_shutdown:
        ready_sockets, _, _ = select.select(subscribed_sockets, [], [], timeout)

        radio_idx = 0
        for client in subscribed_sockets:
            try:
                if client in ready_sockets:
                    rcvdata, _ = client.recvfrom(1)
                    update_radio_membership(radio_idx, int(rcvdata.decode()))
                else:
                    update_radio_membership(radio_idx, -1)
            except socket.timeout:
                print(
                    "[WARNING] PREF Socket Timed out")  # sanity check, it shouldn't ever reach here due to select-checking
                if channel_prefs[radio_idx] != -1:
                    update_radio_membership(radio_idx, -1)
            # TODO: add exception clause for typecast exception
            radio_idx += 1
        time.sleep(sleep)


# driver function
def main():
    server_socket = server_multicast_setup(ttl=TTL, timeout=TIMEOUT)
    channelprefs_sockets = subscription_multicast_setup(multicast_ip=MULTICAST_IP,
                                                        subscription_ports=CHANNEL_PREF_PORTS)
    radio_mic_sockets = subscription_multicast_setup(multicast_ip=MULTICAST_IP, subscription_ports=RADIO_MIC_PORTS)

    channel_prefs_receiving_thread = Thread(target=channel_pref_thread
                                            , args=(channelprefs_sockets,))

    receiving_thread = Thread(target=receiver_thread
                              , args=(radio_mic_sockets, server_socket, TIMEOUT, CHUNK, RCV_MULTIPLIER,))

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

    # start spawning all the core threads
    channel_prefs_receiving_thread.start()
    receiving_thread.start()

    # don't let main thread die
    while True:
        signal.pause()


if __name__ == "__main__":
    main()
