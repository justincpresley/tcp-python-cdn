from argparse import ArgumentParser, SUPPRESS
import socket
import sys
import logging
import threading
import time
from utils.packet_functions import *
from utils.basic_functions import *

def main():
    # Command line parser
    parser = ArgumentParser(add_help=False,description="Ping a port on a certain network")
    requiredArgs = parser.add_argument_group("required arguments")
    optionalArgs = parser.add_argument_group("optional arguments")
    # Adding All command line arguments
    requiredArgs.add_argument("-s","--server",required=True,help="the IP address of the load balancer")
    requiredArgs.add_argument("-p","--port",required=True,type=int,help="the port the server listens on, must be integer")
    requiredArgs.add_argument("-l","--logfile",required=True,help="where it will keep a record of actions")
    optionalArgs.add_argument("-h","--help",action="help",default=SUPPRESS,help="show this help message and exit")
    # Getting All arguments
    args = vars(parser.parse_args())

    # Relaying ALL arguments into variables
    if args["port"] < 0 or args["port"] > 65535:
        logging.error(f'Incorrect port number {args["port"]} not in 0-65535.')
        exit()

    server = args["server"]
    port = int(args["port"])
    logpath = str(args["logfile"])
    webpage = "website.html"

    if validate_ip(server) == False:
        logging.error(f'Not a validate ip4.')
        exit()

    # Logging setup
    logging.basicConfig(level=logging.NOTSET,filename=logpath,filemode='w',format='%(message)s')

    # Client setup
    logging.info(f'Client: starting socket to load balancer')
    sourceSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    contactSock = (server, port)
    sourceSock.connect(contactSock)

    # Communications
    pref_server_ip = "0.0.0.0"
    logging.info(f'Client: starting to communicate')
    try:
        packet = receive_packet(sourceSock)
        pref_server_ip = payload_from_packet(packet).decode()
        logging.info(f'Client: received {pref_server_ip}')
    finally:
    # Close socket
        logging.info(f'Client: stopping socket to load balancer')
        close_socket(sourceSock)

    if pref_server_ip == "0.0.0.0" or pref_server_ip == "":
        logging.info(f'Load Balancer could not connect to any servers, ty again later.')
        exit()

    # Client setup
    logging.info(f'Client: starting socket to prefered server')
    sourceSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    contactSock = (pref_server_ip, port)
    sourceSock.connect(contactSock)

    # Communications
    try:
        logging.info(f'Client: starting to communicate')
        send_packet(sourceSock, form_packet(12345,0,b'',syn=True))
        logging.info(f'SEND   {12345} {0} ACK={"Y "if False else "N"} SYN={"Y" if True else "N"} FIN={"Y" if False else "N"}')
        flag = False
        while not flag:
            packet = receive_packet(sourceSock)
            logging.info(f'RECV   {ack_num_from_packet(packet)} {seq_num_from_packet(packet)+sys.getsizeof(payload_from_packet(packet))} ACK={"Y "if True else "N"} SYN={"Y" if False else "N"} FIN={"Y" if False else "N"}')
            push_bytes_to_file(webpage,payload_from_packet(packet))

            if not fin_flag_from_packet(packet):
                send_packet(sourceSock, form_packet(ack_num_from_packet(packet), seq_num_from_packet(packet)+sys.getsizeof(payload_from_packet(packet)),b'',ack=True))
            else:
                flag = True
                send_packet(sourceSock, form_packet(ack_num_from_packet(packet), seq_num_from_packet(packet)+sys.getsizeof(payload_from_packet(packet)),b'',ack=True, fin=True))
            logging.info(f'SEND   {ack_num_from_packet(packet)} {seq_num_from_packet(packet)+sys.getsizeof(payload_from_packet(packet))} ACK={"Y "if True else "N"} SYN={"Y" if False else "N"} FIN={"Y" if True else "N"}')
    finally:
    # Close socket
        logging.info(f'Client: stopping socket to prefered server')
        close_socket(sourceSock)


if __name__ == '__main__':
    main()