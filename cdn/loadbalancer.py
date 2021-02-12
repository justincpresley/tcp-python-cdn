#    TCP Content Delivery Network
#    Author:  Justin C Presley
#    Github:  https://github.com/justincpresley
#    Contact: justincpresley@gmail.com

from argparse import ArgumentParser, SUPPRESS
import socket
import logging
import time
import ctypes
import subprocess
import re
from utils.packet_functions import *
from utils.basic_functions import *
import threading

server_map = {}

def update_server_map():
    logging.info(f'---')
    global server_map
    IPAddresses = dickeys_into_list(server_map)
    fileOut = "Pingout.dat"
    fileErr = "Pingerr.dat"

    # Ping All the Addresses
    with open(fileOut,"wb") as out, open(fileErr,"wb") as err:
        for i in range(len(IPAddresses)):
            subprocess.run('ping -c 4 ' + IPAddresses[i], stdout=out, stderr=err, shell=True)

    # Finding All the Losses
    lossArray = []
    pattern = re.compile('received, ')
    for line in open(fileOut):
	    for match in re.finditer(pattern, line):
	        lossArray.append(line.split('received, ')[1].split('%')[0])
    loss = [int(i) for i in lossArray]
    logging.info('PingThread: losses (as int):  ' + str(loss))

    # Finding All the Average Times
    avgTimeArray = []
    pattern = re.compile(', time ')
    for line in open(fileOut):
	    for match in re.finditer(pattern, line):
		    avgTimeArray.append(line.split(', time ')[1].split('ms')[0])
    avgTime = [int(i) for i in avgTimeArray]
    logging.info('PingThread: Avg response time (in ms): ' + str(avgTime))

    # Updating All the Preferences
    for key in server_map:
        server_map[key] = (0.75*loss[IPAddresses.index(key)]) + (0.25*avgTime[IPAddresses.index(key)])

    delete_file_in_cwd(fileErr)
    delete_file_in_cwd(fileOut)

def find_best_server_ip():
    global server_map
    best_ip = "0.0.0.0"
    best_pref = 0.00
    for key in server_map:
        if server_map[key] != 0.0:
            if best_pref != 0.00:
                if server_map[key] < best_pref:
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
        global server_map
        best_ip = find_best_server_ip()
        while best_ip=="0.0.0.0":
            logging.info(f'ClientThread: Found the best server as "0.0.0.0", retrying...')
            time.sleep(5)
            best_ip = find_best_server_ip()
        data = best_ip.encode('utf-8')
        send_packet(self.socket, form_packet(1,1,data,syn=True))
        logging.info(f'Request from {self.ip} for <URL>. Redirecting to {best_ip}. Preference {server_map[best_ip]}.')
        logging.info(f'Response from {best_ip} sending request to {self.ip}.')
        self.socket.close()
        logging.info(f'[-] Thread ended for {self.ip}, {str(self.port)}')

class PingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        logging.info(f'[+] New thread started for pinging the servers')
    def run(self):
        try:
            while self.running:
                update_server_map()
                logging.info(f'PingThread: Server Preferences are Updated')
                logging.info(f'PingThread: {server_map}')
                time.sleep(3) # in seconds how long to wait
        finally:
            pass
    def stop(self):
        self.running = False

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
    logging.info(f'Avaliable Servers from Log: {list_of_servers}')

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

    pthread.stop()
    pthread.join()
    for t in cthreads:
        t.join()
    close_socket(sourceSock)

if __name__ == '__main__':
    main()
