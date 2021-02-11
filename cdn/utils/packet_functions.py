#    TCP Content Delivery Network
#    Author:  Justin C Presley
#    Github:  https://github.com/embersight
#    Contact: justincpresley@gmail.com

import socket
import struct
from enum import Enum

class PacketSizes(Enum):
    # Byte Sizes
    SEQ_NUM        = struct.calcsize("I")
    ACK_NUM        = struct.calcsize("I")
    FIRST_HEADER   = SEQ_NUM + ACK_NUM
    LAST_HEADER    = 4
    HEADER         = FIRST_HEADER + LAST_HEADER
    BODY           = 512
    FULL           = HEADER + BODY

    # Numbers
    FLAGS          = 3
    UNUSED_BITS    = 29

# bit string and byte functions
def bitstring_to_bytes(s):
    return int(s, 2).to_bytes(len(s) // 8, byteorder='big')
def bytes_to_bitstring(s):
    result = ""
    for byte in s:
        result += "{:08b}".format(int(bytes([byte]).hex(),16))
    return result

# packet functions
def form_packet(seq_num, ack_num, payload, ack=False, syn=False, fin=False):
    unused = '0' * PacketSizes.UNUSED_BITS.value
    ack_flag = '1' if ack==True else '0'
    syn_flag = '1' if syn==True else '0'
    fin_flag = '1' if fin==True else '0'
    flags = ack_flag + syn_flag + fin_flag

    first_head = struct.pack("II", seq_num, ack_num)
    last_head = bitstring_to_bytes(unused+flags)
    return (first_head+last_head+payload)
def seq_num_from_packet(packet):
    seq_num, ack_num = struct.unpack("II", packet[:PacketSizes.FIRST_HEADER.value])
    return seq_num
def ack_num_from_packet(packet):
    seq_num, ack_num = struct.unpack("II", packet[:PacketSizes.FIRST_HEADER.value])
    return ack_num
def payload_from_packet(packet):
    return packet[PacketSizes.HEADER.value:]
def ack_flag_from_packet(packet):
    flags = bytes_to_bitstring(packet[PacketSizes.FIRST_HEADER.value:PacketSizes.HEADER.value])
    flags = flags[-PacketSizes.FLAGS.value:]
    return True if flags[0]=='1' else False
def syn_flag_from_packet(packet):
    flags = bytes_to_bitstring(packet[PacketSizes.FIRST_HEADER.value:PacketSizes.HEADER.value])
    flags = flags[-PacketSizes.FLAGS.value:]
    return True if flags[1]=='1' else False
def fin_flag_from_packet(packet):
    flags = bytes_to_bitstring(packet[PacketSizes.FIRST_HEADER.value:PacketSizes.HEADER.value])
    flags = flags[-PacketSizes.FLAGS.value:]
    return True if flags[2]=='1' else False

# connection functions
def send_packet(connection, packet):
    connection.send(packet)
def receive_packet(connection):
    packet = connection.recv(PacketSizes.FULL.value)
    return packet
def close_socket(connection):
    try:
        connection.shutdown(socket.SHUT_RDWR)
    except:
        pass
    try:
        connection.close()
    except:
        pass
