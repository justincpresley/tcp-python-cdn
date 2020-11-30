<h1>Python Content Delivery Network</h1>


There are three different programs included that all must be used in order to model a CDN.

A **client**, **loadbalancer**, and a **server**. There can be multiple clients and servers. Also note,

that there can be mutliple clients at the same time at all points of contact. No worries there!



The **Servers** will just simply server a webpage of their choice for whoever wants it.

The **LoadBalancer** will be the main go-to. It will periodically ping each server and test which

one has the best connection / lightest load. Whoever contacts the LoadBalancer will recieve

the best server available's ip.

The **Client** is used to contact a loadbalancer.


Below is the appropriate commands and notes for each part.

This is for Starting the programs. Please view the Shutdown portion as well.




<h2>Client - (should be started last)</h2>

  syntax:  "python3 client.py -s SERVER -p PORT -l LOGFILE"
  
  example: "python3 client.py -s 196.24.12.12 -p 33000 -l log"
  

  The SERVER should be the ip of the loadbalancer that you are using.
  The PORT should be the port used on all the servers and the loadbalancer and what ip the client uses to connect.
  The LOGFILE can be named anything as it is a file created on host, log is preferred.


  Notes: LoadBalancer needs to at least be up. It will wait infinitely if
  there has yet to be any servers up.


<h2>Load Balancer - (best to start after servers are up)</h2>

  syntax:  "python3 loadbalancer.py -s SERVERS -p PORT -l LOGFILE"
  
  example: "python3 loadbalancer.py -s servers.txt -p 33000 -l log"


  The SERVERS should be the file that contains all the ips of the servers.
  (servers.txt is included and should be used)
  The PORT should be the port used on all the servers and the loadbalancer and what ip the client uses to connect.
  The LOGFILE can be named anything as it is a file created on host, log is preferred.


  Notes: Update servers.txt with all the ips of the servers you want to use before you run this.


<h2>Servers - (best to start first)</h2>

  syntax:  "python3 replicaserver.py -p PORT -l LOGFILE -w WEBPAGE"
  
  example: "python3 replicaserver.py -p 33000 -l log -w www.nytimes.com"


  The PORT should be the port used on all the servers and the loadbalancer and what ip the client uses to connect.
  The LOGFILE can be named anything as it is a file created on host, log is preferred.
  The WEBPAGE is the webpage you what the server to server.


  Notes: None.




<h2>SHUTING DOWN THE PROGRAMS PROPERLY</h2>

The Best way to shut down this network is to hit "CTRL C" once or send a keyboard interruption once
to the loadbalancer.py. This will stop severing new clients, but still server the remaining clients.


After this, you can shut down each server with one "CRTL C" or a keyboard interruption. This will, like the
loadbalancer.py, stop any new clients from coming in. However, it will finish serving the remaining clients.


After all that, you can close the client.py with "CRTL C" or a keyboard interruption.




