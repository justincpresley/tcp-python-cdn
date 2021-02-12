<h1>tcp-python-cdn: A Content Delivery Network based on TCP-IP built in python</h1>


There are three different programs included that all must be used in order to model a CDN.<br>
A **client**, **loadbalancer**, and a **server**. There can be multiple clients and servers. Also note,<br>
that there can be mutliple clients at the same time at all points of contact. No worries there!<br>
<br>
The **Servers** will just simply server a webpage of their choice for whoever wants it.<br>
<br>
The **LoadBalancer** will be the main go-to. It will periodically ping each server and test which
one has the best connection / lightest load. Whoever contacts the LoadBalancer will recieve
the best server available's ip.<br>
<br>
The **Client** is used to contact a loadbalancer.<br>
<br>
Below is the appropriate commands and notes for each part.<br>
This is for Starting the programs. Please view the Shutdown portion as well.<br>

---

<h2>Client - (should be started last)</h2>

     syntax:  "python3 client.py -s SERVER -p PORT -l LOGFILE"
  
     example: "python3 client.py -s 196.24.12.12 -p 33000 -l log"
  
  The *SERVER* should be the ip of the loadbalancer that you are using.<br>
  The *PORT* should be the port used on all the servers and the loadbalancer and what ip the client uses to connect.<br>
  The *LOGFILE* can be named anything as it is a file created on host, log is preferred.<br>
  <br>
  Notes: LoadBalancer needs to at least be up. It will wait infinitely if
  there has yet to be any servers up.

---

<h2>Load Balancer - (best to start after servers are up)</h2>

     syntax:  "python3 loadbalancer.py -s SERVERS -p PORT -l LOGFILE"
  
     example: "python3 loadbalancer.py -s servers.txt -p 33000 -l log"

  The *SERVERS* should be the file that contains all the ips of the servers.
  (servers.txt is included and should be used)<br>
  The *PORT* should be the port used on all the servers and the loadbalancer and what ip the client uses to connect.<br>
  The *LOGFILE* can be named anything as it is a file created on host, log is preferred.<br>
  <br>
  Notes: **Update servers.txt** with all the ips of the servers you want to use before you run this.

---

<h2>Servers - (best to start first)</h2>

     syntax:  "python3 replicaserver.py -p PORT -l LOGFILE -w WEBPAGE"
  
     example: "python3 replicaserver.py -p 33000 -l log -w www.nytimes.com"

  The *PORT* should be the port used on all the servers and the loadbalancer and what ip the client uses to connect.<br>
  The *LOGFILE* can be named anything as it is a file created on host, log is preferred.<br>
  The *WEBPAGE* is the webpage you what the server to server.<br>
  <br>
  Notes: None.

---


<h2>SHUTING DOWN THE PROGRAMS PROPERLY</h2>

The Best way to shut down this network is to hit "CTRL C" once or send a **keyboard interruption** once
to the **loadbalancer.py**. This will stop severing new clients, but still server the remaining clients.<br>
<br>
After this, you can shut down each server with one "CRTL C" or a **keyboard interruption**. This will, like the
loadbalancer.py, stop any new clients from coming in. However, it will finish serving the remaining clients for each **server.py**.<br>
<br>
After all that, you can close the **client.py** with "CRTL C" or a **keyboard interruption**.

<h2>License and Authors</h2>

tcp-python-cdn is an open source project that is licensed. See [`LICENSE.md`](LICENSE.md) for more information.

The Names of all authors associated with this project are below:

  * *Justin Presley* (justincpresley)
