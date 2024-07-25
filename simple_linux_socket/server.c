// compile by `gcc -o server server.c`

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <strings.h>
#include <sys/socket.h>
#include <resolv.h>
#include <arpa/inet.h>
#include <errno.h>

#define MY_PORT		9999
#define MAX_BUF		1024

int main()
{
    int sockfd;
	struct sockaddr_in self;
	char buffer[MAX_BUF];

    // To create a socket for networking communication. A new socket by itself is not particularly useful
    sockfd = socket(AF_INET, SOCK_STREAM, 0);

	/** Initialize address/port structure */
	bzero(&self, sizeof(self));
	self.sin_family = AF_INET;
	self.sin_port = htons(MY_PORT);
	self.sin_addr.s_addr = INADDR_ANY;

    // The bind call associates an abstract socket with an actual network interface and port
    bind(sockfd, (struct sockaddr*)&self, sizeof(self));

    // The listen call specifies the queue size for the number of incoming, unhandled connections
	listen(sockfd, 40);

	/** Server run continuously */
	while (1)
	{	int clientfd;
		struct sockaddr_in client_addr;
		int addrlen=sizeof(client_addr);

		/** accept an incomming connection  */
		clientfd = accept(sockfd, (struct sockaddr*)&client_addr, &addrlen);
		printf("%s:%d connected\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

		/** print the received data to the client */
		int read_bytes = read(clientfd, buffer, MAX_BUF);
		printf("Got client message: %s\n", buffer);
		write(clientfd, buffer, read_bytes);

		/** Close data connection */
		close(clientfd);
	}

	/** Clean up */
	close(sockfd);
	return 0;
}