import pyaudio
import numpy as np
import socket
import select
from threading import Thread, Lock
import struct
import signal
import sys
import time

# general UDP segment parameters
CHUNK = 64
RCV_MULTIPLIER = 2  # 2 works well on mac, 4 works better on pi
RATE = 16000  # to be adjusted according to available sound-card
TIMEOUT = 0.01  # receiver select-check timeout
TTL = struct.pack('b', 1)  # udp datagram time-to-live

MULTICAST_IP = '224.3.29.71'
SENDER_PORT = 10101
RECEIVER_PORT = 10400 # TODO: change this after testing
CHANNEL_PREF_PORT = 10301

CHANNEL_PORTS = [10400, 10401, 10402]

channel_preference = 0

# sender
server_multicast_group = (MULTICAST_IP, SENDER_PORT)
channel_multicast_group = (MULTICAST_IP, CHANNEL_PREF_PORT)

# receiver
multicast_group = MULTICAST_IP

not_shutdown = True


def IO_setup(rate, frames_per_buffer, channels=1, type_format=pyaudio.paInt16):
    """Initializes pyaudio reference, then opens streams to I/O devices (ie. microphone and speaker), along with
    respective mutex locks.

    :param rate: sampling rate used for recording and playback streams
    :param frames_per_buffer: buffer parameter for both mic and speaker streams
    :param channels: number of channels
    :param type_format: data format returned from stream
    :return:
        - p - pyaudio reference
        - stream - pyaudio input stream from microphone
        - player - pyaudio output stream to speaker
        - stream_lock - mutex lock for stream
        - player_lock - mutex lock for player
    """
    p = pyaudio.PyAudio()

    stream = p.open(format=type_format
                    , rate=rate
                    , channels=channels
                    , input_device_index=2
                    , input=True
                    , frames_per_buffer=frames_per_buffer)
    player = p.open(format=type_format
                    , rate=rate
                    , channels=channels
                    , output_device_index=1
                    , output=True
                    , frames_per_buffer=frames_per_buffer)

    stream_lock, player_lock = Lock(), Lock()
    return p, stream, player, stream_lock, player_lock


def server_multicast_setup(ttl, timeout):
    """Returns a server socket (UDP multicast).

    :param ttl: struct denoting number of "network layers" before datagram expires
    :param timeout: socket timeout in seconds
    :return: server socket
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    server.settimeout(timeout)
    return server


def subscription_multicast_setup(multicast_ip, port):
    """Returns a UDP multicast socket initialized based on a single IP and port.

    :param multicast_ip: multicast IP address as string
    :param port: integer port number
    :return: a non-blocking multicast socket corresponding to the supplied IP and port
    """
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

    return client


def multi_subscription_multicast_setup(multicast_ip, subscription_ports):
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


def server_thread(server_socket, stream, stream_lock, chunk_size, server_multicast_group):
    """Publishes all microphone audio data from stream to the specified UDP group. Designed to be run as an independent
    thread.

    :param server_socket: server socket used to send data
    :param stream: reference to the input pyaudio stream for the microphone
    :param stream_lock: mutex lock associated with the stream
    :param chunk_size: size of data to acquire from stream in a single read
    :param server_multicast_group: client UDP group in form (MULTICAST_IP, PORT)
    """
    global not_shutdown
    while not_shutdown:  # need to set flag for power-on/power-off
        try:
            data_string = read_from_stream(stream, stream_lock, chunk_size)
            # data = np.fromstring(data_string, dtype=np.int16)
            # print(data)
            server_socket.sendto(data_string, server_multicast_group)
        except socket.timeout:
            pass


def read_from_stream(stream, lock, chunk_size):
    """Thread-safe function for reading from a stream.

    :param stream: stream from which data is to be read
    :param lock: mutex lock associated with the stream
    :param chunk_size: data buffer length to be read
    :return: data read from the stream (byte format)
    """
    lock.acquire()
    data = stream.read(chunk_size, exception_on_overflow=False)
    lock.release()
    return data


def receiver_thread(receiver_socket, player, player_lock, timeout, chunk_size, rcv_multiplier):
    """Receives data response from the central server, and streams it back to the player. Designed to be run as an
    independent thread.

    :param receiver_socket: socket to listen to for data
    :param player: pyaudio stream to output devices (ie. speakers)
    :param player_lock: mutex lock associated with the player
    :param timeout: timeout when checking for data availability on receiver_socket
    :param chunk_size: buffer length to be read from the socket
    :param rcv_multiplier: multiplier for the read buffer length. no effect if set to 1.
    """
    global not_shutdown
    while not_shutdown:  # need to set flag for poweron/off
        ready, _, _ = select.select([receiver_socket], [], [],
                                    timeout)  # check if any data present in subscribed sockets
        try:
            if (receiver_socket in ready):  # if socket has data
                rcvdata, addr = receiver_socket.recvfrom(chunk_size * rcv_multiplier)
                play_sound(player=player, lock=player_lock, data=rcvdata)
        except socket.timeout:
            pass


def play_sound(player, lock, data):
    """Thread-safe function for playing back data to the player streams.

    :param player: pyaudio stream to output devices (ie. speakers)
    :param lock: mutex lock associated with the player
    :param data: data to be streamed (byte format)
    """
    
    lock.acquire()
    player.write(data)
    lock.release()


def channel_preference_thread(channel_socket, channel_multicast_group):
    """Publishes channel preference data to the central server to indicate membership of radio, as well as to signal
    that the radio is still alive and connected. Designed to be run as an independent thread.

    :param channel_socket: socket used to publish channel data
    :param channel_multicast_group: UDP group of the form (MULTICAST_IP, PORT) for data to be sent to
    """
    global channel_preference, not_shutdown
    while not_shutdown:
        try:
            data = str(channel_preference)
            channel_socket.sendto(data.encode(), channel_multicast_group)
            time.sleep(0.1)
        except socket.timeout:
            pass


# driver function
def main():
    p, stream, player, stream_lock, player_lock = IO_setup(rate=RATE, frames_per_buffer=CHUNK)
    server_socket = server_multicast_setup(ttl=TTL, timeout=TIMEOUT)
    channelpref_socket = server_multicast_setup(ttl=TTL, timeout=TIMEOUT)
    receiver_socket = subscription_multicast_setup(multicast_ip=MULTICAST_IP, port=RECEIVER_PORT)

    sending_thread = Thread(target=server_thread
                            , args=(server_socket, stream, stream_lock, CHUNK, server_multicast_group,))

    channelpref_thread = Thread(target=channel_preference_thread
                                , args=(channelpref_socket, channel_multicast_group,))

    receiving_thread = Thread(target=receiver_thread
                              , args=(receiver_socket, player, player_lock, TIMEOUT, CHUNK, RCV_MULTIPLIER,))

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
        channelpref_socket.close()

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
