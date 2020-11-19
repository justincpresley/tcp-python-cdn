from argparse import ArgumentParser, SUPPRESS
import socket
import logging
from utils.packet_functions import *
from utils.basic_functions import *

def startServer(server, port):
    try:
        logging.info(f'Server: starting socket')
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.info(f'Server: binding socket')
        serverSock.bind((server, port))
        logging.info(f'Server: binded socket')
        return serverSock
    except serverSock.error as msg:
        print ('Bind failed. Error Code: ' + str(msg[0]) + 'ERROR: ' + msg[1])
        try:
            serverSock.exit
        except:
            pass
def receive_and_send(serverSock, clientSock, syn_num, ack_num, payload, syn=False, ack=False, fin=False):
    while True:
        serverSock.settimeout(0.5)
        try:
            packet, addr = receive_packet_and_addr(serverSock)
            logging.info(f'RECV   {syn_num} {ack_num} ACK={"Y "if ack else "N"} SYN={"Y" if syn else "N"} FIN={"Y" if fin else "N"}')
            if seq_num_from_packet(packet) != ack_num:
                raise socket.timeout
            break
        except socket.timeout as e:
            send_packet(serverSock, clientSock, form_packet(syn_num, ack_num, b'', syn=syn, ack=ack, fin=fin))
            logging.info(f'RETRAN {syn_num} {ack_num} ACK={"Y "if ack else "N"} SYN={"Y" if syn else "N"} FIN={"Y" if fin else "N"}')
            pass
    return (packet, addr)
def on_client(serverSock, packet, clientSock, num_packets, cached_file):
    send_packet(serverSock, clientSock, form_packet(100, seq_num_from_packet(packet)+1,b'', syn=True, ack=True))
    logging.info(f'SEND   {100} {seq_num_from_packet(packet)+1} ACK={"Y "if True else "N"} SYN={"Y" if True else "N"} FIN={"Y" if False else "N"}')
    packet, addr = receive_and_send(serverSock, clientSock, 100, seq_num_from_packet(packet)+1, b'', syn=True, ack=True)

    for x in range(num_packets):
        bytes = read_bytes_chunk_from_file(cached_file, chunk_size=512, chunk=x)
        if x<(num_packets-1):
            send_packet(serverSock, clientSock, form_packet(ack_num_from_packet(packet), seq_num_from_packet(packet)+1,bytes, syn=True))
            logging.info(f'SEND   {ack_num_from_packet(packet)} {seq_num_from_packet(packet)+1} ACK={"Y "if False else "N"} SYN={"Y" if True else "N"} FIN={"Y" if False else "N"}')
            packet, clientSock = receive_and_send(serverSock, clientSock, ack_num_from_packet(packet), seq_num_from_packet(packet)+1, bytes, syn=True)
        else:
            send_packet(serverSock, clientSock, form_packet(ack_num_from_packet(packet), seq_num_from_packet(packet)+1,bytes, syn=True, fin=True))
            logging.info(f'SEND   {ack_num_from_packet(packet)} {seq_num_from_packet(packet)+1} ACK={"Y "if False else "N"} SYN={"Y" if True else "N"} FIN={"Y" if True else "N"}')

def main():
    # Command line parser
    parser = ArgumentParser(add_help=False,description="Anon Server, A Premitive Proxy")
    requiredArgs = parser.add_argument_group("required arguments")
    optionalArgs = parser.add_argument_group("optional arguments")
    # Adding All command line arguments
    requiredArgs.add_argument("-p","--port",required=True,type=int,help="the port the server listens on, must be an integer")
    requiredArgs.add_argument("-l","--logfile",required=True,help="where it will keep a record of actions")
    requiredArgs.add_argument("-w","--webpage",required=True,help="which webpage to download and serve")
    optionalArgs.add_argument("-h","--help",action="help",default=SUPPRESS,help="show this help message and exit")
    # Getting All arguments
    args = vars(parser.parse_args())

    # Declare basic variables
    if args["port"] < 0 or args["port"] > 65535:
        logging.error(f'Incorrect port number {args["port"]} not in 0-65535.')
        exit()

    server = socket.gethostbyname(socket.gethostname())
    port = int(args["port"])
    logpath = str(args["logfile"])
    webpage = str(args["webpage"])
    webpage = make_proper_url(webpage)
    cached_file = "cached_webpage.html"

    # Logging setup
    logging.basicConfig(level=logging.NOTSET,filename=logpath,filemode='w',format='%(message)s')

    # Cache the website and Calculate
    download_url(webpage, cached_file)
    num_packets = how_many_chunks_in_file(cached_file, chunk_size=PacketSizes.BODY.value)

    # Server start
    serverSock = startServer(server, port)

    # Start communicating
    logging.info(f'Server: listening')
    while True:
        serverSock.settimeout(None)
        packet, addr = receive_packet_and_addr(serverSock)
        logging.info(f'RECV   {seq_num_from_packet(packet)} {ack_num_from_packet(packet)} ACK={"Y "if ack_flag_from_packet(packet) else "N"} SYN={"Y" if syn_flag_from_packet(packet) else "N"} FIN={"Y" if fin_flag_from_packet(packet) else "N"}')
        on_client(serverSock, packet, addr, num_packets, cached_file)

    # Close Socket
    close_socket(serverSock)

    # Delete Cache
    delete_file_in_cwd(cached_file)

if __name__ == '__main__':
    main()