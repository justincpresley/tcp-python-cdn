from argparse import ArgumentParser, SUPPRESS
import socket
import logging
import threading
from _thread import *
import time
from utils.packet_functions import *
from utils.basic_functions import *

print_lock = threading.Lock()

def multi_threaded_client(connection):
    while True:
        packet = receive_packet(connection)
        print(f'{connection} said {payload_from_packet(packet).decode()}')
    connection.close()


def main():
    # Command line parser
    parser = ArgumentParser(add_help=False,description="Ping a port on a certain network")
    requiredArgs = parser.add_argument_group("required arguments")
    optionalArgs = parser.add_argument_group("optional arguments")
    # Adding All command line arguments
    requiredArgs.add_argument("-s","--servers",required=True,help="file that contains all server ips")
    requiredArgs.add_argument("-p","--port",required=True,type=int,help="the port the servers listens on, must be integer")
    requiredArgs.add_argument("-l","--logfile",required=True,help="where it will keep a record of actions")
    optionalArgs.add_argument("-h","--help",action="help",default=SUPPRESS,help="show this help message and exit")
    # Getting All arguments
    args = vars(parser.parse_args())

    # Relaying ALL arguments into variables
    if args["port"] < 0 or args["port"] > 65535:
        logging.error(f'Incorrect port number {args["port"]} not in 0-65535.')
        exit()

    servers_file = args["servers"]
    port = int(args["port"])
    logpath = str(args["logfile"])

    # Logging setup
    logging.basicConfig(level=logging.NOTSET,filename=logpath,filemode='w',format='%(message)s')

    # Load Balancer Setup
    logging.info(f'LoadBalancer: starting socket')
    sourceSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sourceSock.bind(('localhost',port))

    logging.info(f'LoadBalancer: socket listening')
    sourceSock.listen(10)

    # Communications
    while True:
        c, addr = sourceSock.accept()
        logging.info('Connected to: ' + address[0] + ':' + str(address[1]))
        print_lock.acquire()
        start_new_thread(multi_threaded_client, (c,)) 

    sourceSock.close()

if __name__ == '__main__':
    main()