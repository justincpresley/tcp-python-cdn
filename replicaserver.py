from argparse import ArgumentParser, SUPPRESS
import socket
import logging
import threading
from utils.packet_functions import *
from utils.basic_functions import *

def startServer(server, port):
    try:
        logging.info(f'Server: starting socket')
        sourceSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f'Server: binding socket')
        sourceSock.bind((server, port))
        logging.info(f'Server: binded socket')
        sourceSock.listen(10)
        return sourceSock
    except sourceSock.error as msg:
        print ('Bind failed. Error Code: ' + str(msg[0]) + 'ERROR: ' + msg[1])
        try:
            sourceSock.exit
        except:
            pass

class ClientThread(threading.Thread):
    def __init__(self,ip,port,socket,num_packets,filename):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        self.num_packets = num_packets
        self.filename = filename
        logging.info(f'[+] New thread started for {self.ip}, {str(self.port)}')
    def run(self):
        packet = receive_packet(self.socket)
        for x in range(self.num_packets):
            bytes = read_bytes_chunk_from_file(self.filename, chunk_size=512, chunk=x)
            if x<(self.num_packets-1):
                send_packet(self.socket,form_packet(ack_num_from_packet(packet), seq_num_from_packet(packet)+1,bytes, syn=True))
                logging.info(f'SEND   {ack_num_from_packet(packet)} {seq_num_from_packet(packet)+1} ACK={"Y "if False else "N"} SYN={"Y" if True else "N"} FIN={"Y" if False else "N"}')
                packet = receive_packet(self.socket)
                logging.info(f'RECV   {seq_num_from_packet(packet)} {ack_num_from_packet(packet)} ACK={"Y "if ack_flag_from_packet(packet) else "N"} SYN={"Y" if syn_flag_from_packet(packet) else "N"} FIN={"Y" if fin_flag_from_packet(packet) else "N"}')
            else:
                send_packet(self.socket,form_packet(ack_num_from_packet(packet), seq_num_from_packet(packet)+1,bytes, syn=True, fin=True))
                logging.info(f'SEND   {ack_num_from_packet(packet)} {seq_num_from_packet(packet)+1} ACK={"Y "if False else "N"} SYN={"Y" if True else "N"} FIN={"Y" if True else "N"}')
                packet = receive_packet(self.socket)
                logging.info(f'RECV   {seq_num_from_packet(packet)} {ack_num_from_packet(packet)} ACK={"Y "if ack_flag_from_packet(packet) else "N"} SYN={"Y" if syn_flag_from_packet(packet) else "N"} FIN={"Y" if fin_flag_from_packet(packet) else "N"}')

        self.socket.close()
        logging.info(f'[-] Thread ended for {self.ip}, {str(self.port)}')

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
    serverSock = startServer('', port)

    # Start communicating
    logging.info(f'Server: listening')
    cthreads = []
    while True:
        try:
            (clientsock, (ip, port)) = serverSock.accept()
            newthread = ClientThread(ip, port, clientsock, num_packets, cached_file)
            newthread.start()
            cthreads.append(newthread)
        except KeyboardInterrupt:
            break

    for t in cthreads:
        t.join()
    serverSock.close()

    # Close Socket
    close_socket(serverSock)

    # Delete Cache
    delete_file_in_cwd(cached_file)

if __name__ == '__main__':
    main()