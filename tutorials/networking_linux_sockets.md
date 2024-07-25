# Linux Sockets

A **Socket** is a communication endpoint that allows processes to communicate with each other, either on the same machine or across a network. 
A socket is identified by a unique combination of an **IP address** and a **Port Number**, and it is associated with a particular protocol, usually TCP or UDP.

Linux sockets provide a standardized interface for networking communication, and they are used by many network applications, such as web browsers, email clients, etc...
Sockets can be used to establish connections between **Client** and **Server**, or to implement peer-to-peer communication between two applications.

![][networking_sockets]

## The Client-Server model

Most networking applications today are designed around a client-server relationship.
The **Client** is usually an application acting on behalf of a person, such as a web browser accessing google.com.
The **Server** is generally an application that is providing some service, such as supplying the content of the web page of google.com.

Processes implementing a server might be running as [linux services](linux_processes.md#services), started at boot time, and continue to run until the machine is shutdown.
Usually, clients can use the server's **hostname** (e.g. `google.com`, `console.aws.com`, etc...), which is a friendly known name that can be converted into the IP Address of the server using the **Domain Name Service (DNS)** system.

The below figure illustrates multiple clients communicating with the same server: 

![][networking_client-server]

## Socket communication demonstrated 

This exercise will demonstrate a client-server communication over a TCP socket.
Typically, the server should run on different machine than the client, but it is also possible to run the client and the server on the same machine.

1. Lightly review the code in `simple_linux_socket/server.c`, especially the system calls `socket()`, `accept()`, `bind()`, `listen()`, `recv()`.
2. From your bash terminal, compile the code by `gcc -o server server.c`.
3. Run by `./server`.
4. As a client that want to communicate with the server, use the `nc <server ip> <server port>` command to establish a TCP connection and send data to the server.

As `./server` process is started, it first allocates a `socket`, then `bind`s it to the port `9999`, and begins `listen`ing for connections.
At some point later, the client used the `nc` command to communicate with the client by allocating a socket in its local machine, and requests to connect to port 9999 of the server host.
Because `nc` did not request a particular port number, the kernel provides a random one (`52038` in the below output).
As the client requests the connection, it provides its own IP address and the (randomly assigned) port number to the server.
The server chooses to `accept` the connection.
The established socket is now identified by the combined IP address and port number of both the client and server.

`netstat` is an important command that can be used to display a variety of networking information, including open ports.
When a port is used by a socket, it is referred to as an **open port**.


The below is an output example **from the client machine** that is currently holds an `ESTABLISHED` connection with the server:

```console
myuser@hostname:~$ netstat -tuna
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN     
...
tcp        0      0 172.16.17.74:52038      13.51.197.134:9999      ESTABLISHED    <=====
udp        0      0 127.0.0.53:53           0.0.0.0:*                          
udp        0      0 0.0.0.0:67              0.0.0.0:*                          
...
```

The below is an output example **from the server machine**, while the server is running and connected to the above mentioned client:

```console
ubuntu@13.51.197.134:~$ netstat -tuna
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:9999            0.0.0.0:*               LISTEN     
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN     
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN     
tcp        0      0 172.31.46.24:22         212.50.96.83:39152      ESTABLISHED
tcp        0      0 52 172.31.46.24:22      212.50.96.83:58894      ESTABLISHED
tcp        0      0 172.31.46.24:9999       212.50.96.83:52038      ESTABLISHED     <=====
tcp        0      0 172.31.46.24:38150      54.229.116.227:80       TIME_WAIT  
tcp6       0      0 :::22                   :::*                    LISTEN     
tcp6       0      0 :::80                   :::*                    LISTEN     
udp        0      0 127.0.0.1:323           0.0.0.0:*                          
udp        0      0 127.0.0.53:53           0.0.0.0:*                          
udp        0      0 172.31.46.24:68         0.0.0.0:*                          
udp6       0      0 ::1:323                 :::* 
```

Once the socket is established, the `nc` process and the `./server` process can read information from and write information to one another as easily as reading and writing from a file.

> #### 🧐 Try it yourself - Multiple connections to the same server
>
> Create multiple connections between different clients to the same server.
> Explore the connections in `netstat`'s output.
> 
> Once the server is running, explore `/proc/<pid>/fd` while `<pid>` is the server process id, to see the created socket file.
>


## Well-known and privileged ports, more on `netstat`

Unlike clients, processes implementing the server side, generally request which port they would like to bind to.
Only one process may bind to a port at any given time.


For example, our `simple_socket_server` bound to port `9999`. 
Why `9999`? no any good reason for that. 
but in the Internet, there are well-known port for famous services. 
For example: 

- Servers working with HTTP usually listen on port 80.
- Servers working with HTTPS (HTTP Secure) usually listens on port 443.
- If you connect to a remote machine using the SSH protocol, usually the remote machine is listening to port 22. 


On Linux machines, a catalog of well known services and port can be found in `/etc/services`.

Ports less than `1024` are known as **privileged ports**, and treated specially by the kernel.
Only processes running as the `root` user may bind to privileged ports.

We now analyze a few extracted lines from the above output of the `netstat -tuna` command.

```text 
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp   0      0      0.0.0.0:9999            0.0.0.0:*               LISTEN     
```

This socket is bound to all interfaces (`0.0.0.0` means "all IP addresses") in the `LISTENING` state, one on port `9999`.
This can be recognized as the process of our server that actively listening for client connections.

The next example is listening for connections as well, but only on the loopback address:

```text
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp   0      0      127.0.0.1:631           0.0.0.0:*               LISTEN 
```

It must belong to services expecting to receive connections from other processes on the local machine only. 
To determine what services these ports belong to, we do some `grep`ing from the `/etc/services` file.

```console
ubuntu@13.51.197.134:~$ cat /etc/services | grep 631
ipp		631/tcp				# Internet Printing Protocol
```

Apparently, the process listening on port 631 is listening for print clients. This is probably the `cupsd` printing daemon.

Last example:

```text
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp   0      0      127.0.0.1:631           127.0.0.1:59330         ESTABLISHED     
tcp   0      0      127.0.0.1:59330         127.0.0.1:631           ESTABLISHED     
```

These lines reflect both halves of an established connection between two processes, both on the local machine.
The first is bound to port 59330 (probably a randomly assigned client port), and the second to the port 631.
Some process on the local machine must be communicating with the `cupsd` daemon.


[networking_sockets]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/networking_sockets.png
[networking_client-server]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/networking_client-server.png

