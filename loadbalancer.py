from argparse import ArgumentParser, SUPPRESS
import socket
import logging
import time
from utils.packet_functions import *
from utils.basic_functions import *
import threading

# Logging setup
logging.basicConfig(level=logging.NOTSET,filename=logpath,filemode='w',format='%(message)s')

class ClientThread(threading.Thread):
    def __init__(self,ip,port,socket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        print "[+] New thread started for "+ip+":"+str(port)
    def kill(self):
        self.socket.close()
    def run(self):
        try:
            while True:
                packet = receive_packet(self.socket)
                logging.info(f'{ip} said {payload_from_packet(packet).decode()}')
        except:
            self.kill()

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


    # Load Balancer Setup
    logging.info(f'LoadBalancer: starting socket')
    sourceSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sourceSock.bind(('',port))

    logging.info(f'LoadBalancer: socket listening')
    sourceSock.listen(10)

    # Communications
    while True:
        (clientsock, (ip, port)) = sourceSock.accept()
        newthread = ClientThread(ip, port, clientsock)
        newthread.start()
        threads.append(newthread)

    sourceSock.close()

if __name__ == '__main__':
    main()