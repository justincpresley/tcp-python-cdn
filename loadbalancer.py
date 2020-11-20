from argparse import ArgumentParser, SUPPRESS
import socket
import logging
import time
from utils.packet_functions import *
from utils.basic_functions import *
import threading

server_map = {}

def update_server_map():
    global server_map
    for key in server_map:
        server_map[key] = 1.0
        logging.info(f'servermap {key} now is 1.0')

def find_best_server_ip():
    global server_map
    best_ip = "0.0.0.0"
    best_pref = 0.0
    for key in server_map:
        if server_map[key] != 0.0:
            if best_ip != 0.00:
                if server_map[key] > best_pref:
                    best_pref = server_map[key]
                    best_ip = key
            else:
                best_pref = server_map[key]
                best_ip = key
    return best_ip

class ClientThread(threading.Thread):
    def __init__(self,ip,port,socket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        logging.info(f'[+] New thread started for {self.ip}, {str(self.port)}')
    def run(self):
        best_ip = find_best_server_ip()
        while best_ip=="0.0.0.0":
            time.sleep(5)
            best_ip = find_best_server_ip()
        data = best_ip.encode('utf-8')
        send_packet(self.socket, form_packet(1,1,data,syn=True))
        self.socket.close()
        logging.info(f'[-] Thread ended for {self.ip}, {str(self.port)}')

class PingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        logging.info(f'[+] New thread started for pinging the servers')
    def run(self):
        try:
            while True:
                logging.info(f'Loop for pinging has ran')
                update_server_map()
                time.sleep(10) # in seconds how long to wait
        finally:
            pass

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

    # Logging setup
    logpath = str(args["logfile"])
    logging.basicConfig(level=logging.NOTSET,filename=logpath,filemode='w',format='%(message)s')

    # Relaying ALL arguments into variables
    if args["port"] < 0 or args["port"] > 65535:
        logging.error(f'Incorrect port number {args["port"]} not in 0-65535.')
        exit()

    servers_file = args["servers"]
    port = int(args["port"])
    list_of_servers = file_into_list(servers_file)

    # Make the complex mapping from server list
    global server_map
    for ip in list_of_servers:
        server_map[ip] = 0.00

    # Create a thread to ping and manage servers
    pthread = PingThread()
    pthread.start()

    # Load Balancer Setup
    logging.info(f'LoadBalancer: starting socket')
    sourceSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sourceSock.bind(('',port))

    logging.info(f'LoadBalancer: socket listening')
    sourceSock.listen(10)

    # Communications
    cthreads = []
    while True:
        try:
            (clientsock, (ip, port)) = sourceSock.accept()
            newthread = ClientThread(ip, port, clientsock)
            newthread.start()
            cthreads.append(newthread)
        except KeyboardInterrupt:
            break

    pthread.raise_exception()
    pthread.join()
    for t in cthreads:
        t.join()
    close_socket(sourceSock)

if __name__ == '__main__':
    main()