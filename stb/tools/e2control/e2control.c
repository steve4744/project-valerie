/* 
 * e2control.c
 *
 * Copyright (C) 2004 Marcus Metzler <mocm@metzlerbros.de>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * as published by the Free Software Foundation; either version 2.1
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 *
 */

#include <sys/ioctl.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <time.h>
#include <unistd.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <arpa/inet.h> 

#include <pthread.h>



#define MAX_CHARS_UDP 256
#define MAX_CHARS_TCP 1460

#define UDP_PORT 5450
#define TCP_PORT 5451

#define MAGIC_SERVER_UDP_BROADCAST "SERV_REQ"
#define MAGIC_REQ_PROTOYPE "###########"
#define MAGIC_REQ_FILE_MO "REQ_FILE_MO"
#define MAGIC_REQ_FILE_MT "REQ_FILE_MT"
#define MAGIC_REQ_CMDEXEC "REQ_CMDEXEC"

void *answerUdpBroadcast(void *)
{

	struct sockaddr_in bcast;
	socklen_t len_bcast;

	int bsockfd;

	bsockfd = socket(PF_INET, SOCK_DGRAM, 0);
	len_bcast = sizeof(bcast);

	memset(&bcast, 0, len_bcast);
	bcast.sin_family = AF_INET;
	bcast.sin_port = htons(UDP_PORT);
	bcast.sin_addr.s_addr = htons(INADDR_ANY);
	printf("%s:%d\n", __FUNCTION__, __LINE__);
	if(inet_pton(AF_INET, "255.255.255.255", &bcast.sin_addr) <= 0) {
		printf("inet_pton error\n");
		pthread_exit(NULL);
	}

	printf("%s:%d\n", __FUNCTION__, __LINE__);
	if(bind(bsockfd, (struct sockaddr*)&bcast, len_bcast) <0) {
		printf("bind error\n");
		pthread_exit(NULL);
	}

	while(1)
	{
		int len_adr_client, n;
		struct sockaddr_in bcast, adr_client;
		char dgram[MAX_CHARS_UDP];

		printf("%s:%d\n", __FUNCTION__, __LINE__);
		len_adr_client = sizeof(adr_client);
		if((n=recvfrom(bsockfd, dgram, sizeof(dgram), 0, (struct sockaddr*)&adr_client, (socklen_t*)&len_adr_client))<0) {
			printf("recvfrom failed\n");
			continue;
		}

		dgram[n]='\0';

		printf("%s:%d <- %s\n", __FUNCTION__, __LINE__, dgram);
		if(!strncmp(MAGIC_SERVER_UDP_BROADCAST, dgram, strlen(MAGIC_SERVER_UDP_BROADCAST)))
		{
			//char* s = "MANUFACTOR=Kathrein;MODEL=UFS910;";
			char * s = getenv("BOXSYSTEM");
			printf("%s:%d -> \"%s\" %d\n", __FUNCTION__, __LINE__, s, strlen(s));
			if((n=sendto(bsockfd, s, strlen(s), 0, (struct sockaddr*)&adr_client, len_adr_client))<0) {
				printf("sendto failed\n");
				continue;
			}
			printf("%s:%d sento %d bytes\n", __FUNCTION__, __LINE__, n);
		}

		printf("%s:%d\n", __FUNCTION__, __LINE__);		
	}
	close(bsockfd);
}

void *tcpRequests(void *)
{
	int fdc, fdd, len_local;
	struct sockaddr_in local, remote;
	char string[MAX_CHARS_TCP];

	if ((fdc=socket(PF_INET, SOCK_STREAM, 0)) < 0) {
		perror("tcp socket error");
		pthread_exit(NULL);
	}
	len_local = sizeof(local);
	memset(&local, 0, len_local);
	local.sin_family=AF_INET;
	local.sin_port=htons(TCP_PORT);
	local.sin_addr.s_addr=htonl(INADDR_ANY);
	/*if(inet_pton(AF_INET, "255.255.255.255", &local.sin_addr) <= 0) {
		printf("inet_pton error\n");
		continue;
	}*/
	//memset(&local.sin_zero, 0, sizeof(local.sin_zero));

	// bind and listen on port and ip interface
	if (bind(fdc, (struct sockaddr*)&local, len_local) < 0) {
		perror("tcp bind error");
		pthread_exit(NULL);
	}
	if (listen(fdc, 15) < 0) {
		perror("tcp listen error");
		pthread_exit(NULL);
	}

	while(1) {
		printf("%s:%d\n", __FUNCTION__, __LINE__);
	  	int rlen=sizeof(remote);
		// accept connection
		if ((fdd=accept(fdc, (struct sockaddr*)&remote, (socklen_t*)&rlen)) < 0) {
			perror("accept error");
			continue;
		}

		printf("%s:%d\n", __FUNCTION__, __LINE__);
		//close(fdc);

		printf("Got TCP-Connection from %s\n", inet_ntoa(remote.sin_addr));

		//First of read what the client want
		int slen = read(fdd, string, strlen(MAGIC_REQ_PROTOYPE));
		string[slen] = '\0';

		if(!strncmp(MAGIC_REQ_CMDEXEC, string, slen))
		{
			unsigned char lenArray[2];
			unsigned short lenCmd = 0;
			unsigned int bMsgId = 0;
			char * cmd;

			read(fdd, &lenArray, 2);

			printf("%d %d\n", lenArray[0], lenArray[1]);

			lenCmd = lenArray[0] + (lenArray[1] << 8);

			printf("%d\n", lenCmd);

			cmd = (char*)malloc(lenCmd+1);

			read(fdd, cmd, lenCmd);
			cmd[lenCmd] = '\0';

			printf("CMD: %s\n", cmd);
			FILE * output = popen(cmd, "r");
			
			unsigned char bSendBuffer[MAX_CHARS_TCP];
			unsigned char * p_bSendBuffer = bSendBuffer;
			unsigned int iSendBufferCounter = 0;
			
			int SIZE_LENGTH = 2;
			
			while(!feof(output)) {
				char bLineBuffer[1024]; 
				char * p_bLineBuffer = fgets(bLineBuffer, sizeof(bLineBuffer), output); 

				if(p_bLineBuffer != NULL) {
					int iLineLength = strlen(p_bLineBuffer);
					short sLineLength = iLineLength & 0xFFFF;
					
					//printf("iSendBufferCounter=%d + sLineLength=%d + SIZE_LENGTH=%d > MAX_CHARS_TCP=%d\n",
					//	iSendBufferCounter, sLineLength, SIZE_LENGTH, MAX_CHARS_TCP);
					
					if(iSendBufferCounter + sLineLength + SIZE_LENGTH > MAX_CHARS_TCP)
					{
						printf("Sending %d Bytes\n", iSendBufferCounter);
						write(fdd, p_bSendBuffer, iSendBufferCounter);
						
						iSendBufferCounter = 0;
					}
					
					{
						memcpy(&bSendBuffer[iSendBufferCounter], &sLineLength, SIZE_LENGTH);
						iSendBufferCounter += SIZE_LENGTH;
						
						memcpy(&bSendBuffer[iSendBufferCounter], p_bLineBuffer, sLineLength);
						iSendBufferCounter += sLineLength;
					}
				}
			}
			
			if(iSendBufferCounter > 0)
			{
				printf("Sending Last %d Bytes\n", iSendBufferCounter);
				write(fdd, p_bSendBuffer, iSendBufferCounter);
			}
			
			pclose(output);
		} else if(!strncmp(MAGIC_REQ_FILE_MT, string, slen))
		{
			char * name;

			{
				short lenName = 0;

				read(fdd, &lenName, 2);

				printf("lenName: %hu %04hx\n", lenName, lenName);

				name = (char*)malloc(lenName+1);

				read(fdd, name, lenName);
				name[lenName] = '\0';

				printf("Name: %s\n", name);
			}

			{
				int lenFile = 0;

				read(fdd, &lenFile, 4);

				printf("Filesize: %u %08x\n", lenFile, lenFile);

				char buffer[MAX_CHARS_TCP]; 

				FILE *pFile;
	   			pFile = fopen( name, "w");

				for(int i = 0; i < lenFile;) {
					short bytesToRead = (lenFile - i)>MAX_CHARS_TCP?MAX_CHARS_TCP:lenFile-i;

					//printf("remaining %d [%d]", lenFile - i, bytesToRead);

					read(fdd, &buffer, bytesToRead);
					fwrite (buffer , 1 , bytesToRead , pFile );
					i+=bytesToRead;
				}


				fclose(pFile);

			}


		}

		close(fdd);
	}
	
}



int main(void)
{
	pthread_t answerUdpBroadcastThread;
	pthread_t tcpRequestsThread;
	int error = 0;


	error = pthread_create(&answerUdpBroadcastThread, NULL, answerUdpBroadcast, NULL);
	if(error) printf("Error while creating answerUdpBroadcast Thread!\n");

	error = pthread_create(&tcpRequestsThread, NULL, tcpRequests, NULL);
	if(error) printf("Error while creating answerUdpBroadcast Thread!\n");


	pthread_exit(NULL);
	return 0;
}

