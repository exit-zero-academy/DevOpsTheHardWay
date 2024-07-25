# Networking

This tutorial was built thanks to the great book [Computer Networking: a Top Down Approach](https://gaia.cs.umass.edu/kurose_ross/).

## The OSI model


In order to get data over the network, lots of different hard- and software needs to work and communicate together via a well-defined **protocol**.
A protocol is, simply put, a set of rules for communication. You've probably heard some of them: HTTP, SSH, TCP/IP etc...
All these different types of communication protocols are classified in 7 layers, which are known as the Open Systems Interconnection Reference Model, the OSI Model for short.

In this course we will discuss the 4-layer model, which is a simplified version of the OSI model that combines several of the OSI layers into four layers.

This model is commonly used in the TCP/IP protocol suite, which is the basis for the Internet.

The four layers of the TCP/IP model, in order from top to bottom, are:

| Layer Name              | Common used protocols |
|-------------------------|-----------------------|
| Application Layer       | HTTP, DNS, SMTP, SSH  |
| Transport Layer         | TCP, UDP              |
| Network Layer           | IP, ICMP              |
| Network Interface Layer | Ethernet              |

### Visiting google.com in the browser - it's really much more complicated than it looks!

What happen when you open up your web browser and type http://www.google.com/? We will try to examine it in terms of the OSI model.

#### Application layer

The browser uses HTTP protocol to form an HTTP request to Google's servers, to serve Google's home page. 
The HTTP request is merely a text in a well-defined form, it may look like:

```text
GET / HTTP/1.1
Host: google.com
User-Agent: Mozilla/5.0
```

Note that we literally want to transfer this text to Google's servers, as is.
In the server side, there is an application (called "webserver", obviously) that knows what to do and how to response to this text format.
Since web browser and web servers are applications that use the network, it resides in the Application layer.

The **Application layer** is where network applications and their corresponding protocols reside. Network applications may be web-browsers, web-server, mailing software, and every application that send or receive data over the Internet, in any kind and form.

Do your Firefox or Chrome browsers are responsible for the actual data transfer over the Internet? Hell no.
They both use the great service of the **Transport layer**.

#### Transport layer

After your browser formulated an HTTP text message (a.k.a. **HTTP request**), the message is transferred (by writing it to a file of type **socket** - will be discussed later), to another "piece of software" in the Linux kernel which is responsible for **controlling the transmission** of the Application layer messages to the other host.
The Transmission Control Protocol (TCP) forms the [set of rules](https://www.ietf.org/rfc/rfc793.txt) according which the message is being transferred to the other host, or received from another host. 

TCP breaks long **messages** into shorter **segments**, it guarantees that the data was indeed delivered to the destination and controls the order in which segments are being sent.
Note that TCP only controls **how** the data is being sent and received, but it does not responsible for the actual data transfer. 

Besides TCP, there is another common protocol in the Transport layer which is called **UDP**.

- TCP (Transmission Control Protocol): Reliable, connection-oriented, provides a guaranteed delivery of data and error detection mechanisms. 
- UDP (User Datagram Protocol): Lightweight, connectionless, used for fast, low-latency communication. Commonly used for video streaming, online gaming, and other real-time applications.

To send its data, TCP and UDP use the service of a very close friend - **Internet Protocol (IP)**.


#### Internet layer

We continue our journey to get Google.com's homepage. 
So we have a few segments, ready to be transferred to Google's servers. 

The IP protocol is responsible for moving the TCP segments from one host to another.
Just as you would give the postal service a letter with a destination address, IP protocol sends piece of data (a.k.a **Packets**) to an address (a.k.a **IP address**).
Like TCP and UDP, IP is a piece of software resides in the Linux kernel (so close to TCP, that they are frequently called TCP/IP).
In order to send packets over the Internet, IP communicates with a **Network Interface**, which is a software abstraction that represents a network physical (of virtual) device, such as an Ethernet card or a wireless adapter.

The Network layer routes packets through a series of routers between the source and destination hosts.

#### Network Interface layer

The Network Interface layer is the lower level component in our model. 
It provides an interface between the physical network and the higher-level networking protocols.
It handles the transmission and reception of data (a.k.a. **Frames**) over the network, and it is responsible for converting **digital signals** into **analog signals** for transmission over the physical network.

In this layer, every physical (or virtual) network device has a media access control (**MAC**) address, which is a unique identifier assigned to a network interface. 

# Exercises

### :pencil2: Inspecting OSI layers via WireShark

Wireshark is a popular network protocol analyzer that allows users to capture and inspect network traffic in real time, making it a valuable tool for network troubleshooting and analysis.

Install it on Ubuntu:   
https://www.wireshark.org/docs/wsug_html_chunked/ChBuildInstallUnixInstallBins.html#_installing_from_debs_under_debian_ubuntu_and_other_debian_derivatives

Run it by:

```bash
sudo wireshark
```

Start capturing packets, by clicking on the ![][networking_wiresharkstart] button.
In wireshark, apply(![][networking_wireshark_apply]) the following filter to catch only packets destined for `google.com`:

```text
http.host == "google.com"
```

From your terminal, use the `curl` command to get the main page of `google.com`

```bash
curl google.com
```

Explore the **packet details pane**.

![][networking_wireshark_packet_pane]

This pane displays the contents of the selected packet (packet here is referred to as “any piece of data that traverses down the model layers”).
You can expand or collapse each layer to view the details of the corresponding layer, such as the source and destination addresses, protocol flags, data payloads, and other relevant information.

Based on our discussion on the OSI model, and your previous knowledge in computer networking, try to look for the following information:


1. How many layers does the packet cross?
2. What is the top layer, which is the lower?
3. The “network interface” layer is not part of the original OSI model. It is composed by the two lower layers of the original model, what are those two layers according to the packet details pane on your WireShark screen?
4. How does the original message to google.com (the HTTP request) look like in the top layer?
5. Is the packet sent using TCP or UDP?
6. What is the length of the transport layer segment?
7. To how many segments the original message has been segmented?
8. Which version of IP protocol did you use in the Internet layer?
9. In the Internet layer, what is the destination IP of the packets?
10. What is the MAC address of your device?
11. How many bits have been transmitted over the wire to google's servers?
12. What is the protocol sequence that the frame (the lower level piece of data) have been composed of?  

[networking_wiresharkstart]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/networking_wiresharkstart.png
[networking_wireshark_apply]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/networking_wireshark_apply.png
[networking_wireshark_packet_pane]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/networking_wireshark_packet_pane.png