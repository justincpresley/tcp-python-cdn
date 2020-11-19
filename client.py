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

    # Client Setup
    logging.info(f'Client: starting socket')
    sourceSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    contactSock = (server, port)
    sourceSock.connect(contactSock)

    # Communications
    logging.info(f'Client: starting to communicate')
    try:
        while True:
            string = "HELLO"
            send_packet(sourceSock, form_packet(12345,0,string.encode(),syn=True))
            time.sleep(30)


    finally:
    # Close Socket
        logging.info(f'Client: stopping socket')
        close_socket(sourceSock)

if __name__ == '__main__':
    main()