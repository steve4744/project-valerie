/* 
 * e2control.c
 *
 * Copyright (C) 2010 Schischu <schischu65@gmail.com>
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
#include <arpa/inet.h> 
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <time.h>
#include <unistd.h>
#include <stdlib.h>
//#include <netinet/in.h>

//#include <sys/un.h>

#include <pthread.h>



#define MAX_CHARS_UDP 256
#define MAX_CHARS_TCP 1460

#define CONTROL_PORT 5449
#define UDP_PORT 5450
#define TCP_PORT 5451

#define MAGIC_SERVER_UDP_BROADCAST "SERV_REQ"
#define MAGIC_REQ_PROTOYPE "###########"
#define MAGIC_REQ_FILE_MO "REQ_FILE_MO"
#define MAGIC_REQ_FILE_MT "REQ_FILE_MT"
#define MAGIC_REQ_CMDEXEC "REQ_CMDEXEC"

#define CONTROL_CMD_GETLOGFILENAME 0x00
#define CONTROL_CMD_SHUTDOWN 0x01

//static int fdLogfile = -1;
static FILE * fpLogfile = NULL;
static char * filename = "stdout";

void openLogfile()
{
	filename = tmpnam (NULL);
	//fdLogfile = open(filename, O_WRONLY|O_CREAT);
	fpLogfile = fopen(filename, "w");
	printf ("Logging to: %s\n", filename);
}

void closeLogfile()
{
	fclose(fpLogfile);
}

void printThis( const char* format, ... ) {
    va_list args;

    time_t time_value = time(NULL);
    struct tm *now = localtime(&time_value);
    fprintf(fpLogfile, "%02d:%02d:%02d ", now->tm_hour, now->tm_min, now->tm_sec);

    va_start( args, format );
    vfprintf( fpLogfile, format, args );
    va_end( args );
    fflush(fpLogfile);
}

//#define DEBUG

void dbgprintf( const char* format, ... ) {
#ifdef DEBUG
    va_list args;

    time_t time_value = time(NULL);
    struct tm *now = localtime(&time_value);
    fprintf(stderr, "%02d:%02d:%02d ", now->tm_hour, now->tm_min, now->tm_sec);

    va_start( args, format );
    vfprintf( stderr, format, args );
    va_end( args );
#endif
}

                    /* read n bytes from a socket descriptor */ 
                    int readsock(sockfd, buf, nbytes) 
                    register    int            sockfd; 
                    register    char        *buf; 
                    register    int            nbytes; 
                    { 
                        int nleft, nread; 
                        nleft = nbytes; 
                        while (nleft > 0) { 
                                if ((nread = read(sockfd, buf, nleft)) < 0) 
                                    return(nread); /* error, nread < 0 */ 
                                else if (nread == 0) 
                                    break;    /* EOF */ 
                                /* nread > 0. update nleft and buf pointer */ 
                                nleft -= nread; 
                                buf += nread; 
                        } /* while */ 
                        return(nbytes - nleft); 
                    } /* readsock() */ 
 

void *answerUdpBroadcast(void * none)
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
	printThis("%s:%d\n", __FUNCTION__, __LINE__);
	if(inet_pton(AF_INET, "255.255.255.255", &bcast.sin_addr) <= 0) {
		printThis("inet_pton error\n");
		pthread_exit(NULL);
	}

	printThis("%s:%d\n", __FUNCTION__, __LINE__);
	if(bind(bsockfd, (struct sockaddr*)&bcast, len_bcast) <0) {
		printThis("bind error\n");
		pthread_exit(NULL);
	}

	while(1)
	{
		int len_adr_client, n;
		struct sockaddr_in bcast, adr_client;
		char dgram[MAX_CHARS_UDP];

		printThis("%s:%d\n", __FUNCTION__, __LINE__);
		len_adr_client = sizeof(adr_client);
		if((n=recvfrom(bsockfd, dgram, sizeof(dgram), 0, (struct sockaddr*)&adr_client, (socklen_t*)&len_adr_client))<0) {
			printThis("recvfrom failed\n");
			continue;
		}

		dgram[n]='\0';

		printThis("%s:%d <- %s\n", __FUNCTION__, __LINE__, dgram);
		if(!strncmp(MAGIC_SERVER_UDP_BROADCAST, dgram, strlen(MAGIC_SERVER_UDP_BROADCAST)))
		{
			//char* s = "MANUFACTOR=Kathrein;MODEL=UFS910;";
			char * s = getenv("BOXSYSTEM");
			if(s == NULL || strlen(s) <= 0)
				s = strdup("MANUFACTOR=Testbox;MODEL=TESTBOX;");
			printThis("%s:%d -> \"%s\" %d\n", __FUNCTION__, __LINE__, s, strlen(s));
			if((n=sendto(bsockfd, s, strlen(s), 0, (struct sockaddr*)&adr_client, len_adr_client))<0) {
				printThis("sendto failed\n");
				continue;
			}
			printThis("%s:%d sento %d bytes\n", __FUNCTION__, __LINE__, n);
		}

		printThis("%s:%d\n", __FUNCTION__, __LINE__);		
	}
	close(bsockfd);
}

void * tcpRequests(void * none)
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
		printThis("%s:%d\n", __FUNCTION__, __LINE__);
	  	int rlen=sizeof(remote);
		// accept connection
		if ((fdd=accept(fdc, (struct sockaddr*)&remote, (socklen_t*)&rlen)) < 0) {
			printThis("accept error\n");
			continue;
		}

		printThis("%s:%d\n", __FUNCTION__, __LINE__);
		//close(fdc);

		printThis("Got TCP-Connection from %s\n", inet_ntoa(remote.sin_addr));

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

			printThis("%d %d\n", lenArray[0], lenArray[1]);

			lenCmd = lenArray[0] + (lenArray[1] << 8);

			printThis("%d\n", lenCmd);

			cmd = (char*)malloc(lenCmd+1);

			read(fdd, cmd, lenCmd);
			cmd[lenCmd] = '\0';

			printThis("CMD: %s\n", cmd);
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
					
					//printThis("iSendBufferCounter=%d + sLineLength=%d + SIZE_LENGTH=%d > MAX_CHARS_TCP=%d\n",
					//	iSendBufferCounter, sLineLength, SIZE_LENGTH, MAX_CHARS_TCP);
					
					if(iSendBufferCounter + sLineLength + SIZE_LENGTH > MAX_CHARS_TCP)
					{
						printThis("Sending %d Bytes\n", iSendBufferCounter);
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
				printThis("Sending Last %d Bytes\n", iSendBufferCounter);
				write(fdd, p_bSendBuffer, iSendBufferCounter);
			}
			
			pclose(output);
		} else if(!strncmp(MAGIC_REQ_FILE_MT, string, slen))
		{
			char * name;

			{
				short lenName = 0;

				read(fdd, &lenName, 2);

				printThis("lenName: %hu %04hx\n", lenName, lenName);

				name = (char*)malloc(lenName+1);

				read(fdd, name, lenName);
				name[lenName] = '\0';

				printThis("Name: %s\n", name);
			}

			{
				int lenFile = 0;

				read(fdd, &lenFile, 4);

				printThis("Filesize: %u %08x\n", lenFile, lenFile);

				char buffer[MAX_CHARS_TCP]; 

				FILE *pFile;
	   			pFile = fopen( name, "w");
				int i = 0;
				for(i = 0; i < lenFile;) {
					short bytesToRead = (lenFile - i)>MAX_CHARS_TCP?MAX_CHARS_TCP:lenFile-i;

					//printThis("remaining %d [%d]", lenFile - i, bytesToRead);

					// We cant realy expect to always read a whole array, 
					// so only write the bytes to file which we know that we read
					int realBytesRead = read(fdd, &buffer, bytesToRead);
					fwrite (buffer , 1 , realBytesRead , pFile );
					i += realBytesRead;
				}


				fclose(pFile);

			}


		}

		close(fdd);
	}
	
}

#define SOCKETNAME "/tmp/e2control.socket"
static int vShutdown = 0;


int listenControlSocket(int fdc)
{
	dbgprintf("%s->\n", __FUNCTION__);
	int fdd;
	

	if (listen(fdc, 15) < 0) {
		printThis("listenControlSocket - listen error\n");
	}

	while(1) {
		// accept connection
	dbgprintf("%s->\n", __FUNCTION__);
		struct sockaddr_in socketRemote;
		memset(&socketRemote, 0, sizeof(struct sockaddr_in));
		socklen_t len = sizeof(struct sockaddr_in);
		if ((fdd = accept(fdc, (struct sockaddr*)&socketRemote, &len)) < 0) {
			perror("listenControlSocket - accept error\n");
			continue;
		}
		int cmd = 0;
		read(fdd, &cmd, sizeof(int));
		printThis("Command: %02d\n", cmd);
		switch(cmd)
		{
			case CONTROL_CMD_GETLOGFILENAME: write (fdd, filename, strlen(filename)); break;
			case CONTROL_CMD_SHUTDOWN: vShutdown = 1; break;
			default:
				break;
		}

	dbgprintf("%s-<\n", __FUNCTION__);

		/*printThis("%s:%d\n", __FUNCTION__, __LINE__);
		//close(fdc);

		printThis("Got TCP-Connection from %s\n", inet_ntoa(remote.sin_addr));

		//First of read what the client want
		int slen = read(fdd, string, strlen(MAGIC_REQ_PROTOYPE));*/
	}
	dbgprintf("%s-<\n", __FUNCTION__);
	return 0;
}

int sendControlCommand(int cmd, unsigned char * buffer, int * bufferlen)
{
	dbgprintf("%s->\n", __FUNCTION__);
	struct sockaddr_in serv_addr;
	int sockfd = socket(PF_INET, SOCK_STREAM, 0);
	memset(&serv_addr, 0, sizeof(struct sockaddr_in));
	serv_addr.sin_family = AF_INET; 
	serv_addr.sin_port = htons(CONTROL_PORT);
	serv_addr.sin_addr.s_addr = inet_addr ("127.0.0.1"); 
	socklen_t len = sizeof(struct sockaddr_in);
	if(connect(sockfd, (struct sockaddr *) &serv_addr, len) != 0)
		perror("Connect error\n");

	write(sockfd, &cmd, sizeof(int));
	if(*bufferlen > 0)
		*bufferlen = read(sockfd, buffer, *bufferlen);
	close(sockfd);
	dbgprintf("%s-<\n", __FUNCTION__);
}

int createControlSocket()
{
	dbgprintf("%s->\n", __FUNCTION__);
	int success = 0;

	struct sockaddr_in socketLocal;
	int fdControl = socket(PF_INET, SOCK_STREAM, 0);
	memset(&socketLocal, 0, sizeof(struct sockaddr_in));
	socketLocal.sin_family = AF_INET;
	socketLocal.sin_port = htons(CONTROL_PORT);
	socketLocal.sin_addr.s_addr = htonl(INADDR_ANY);

	if (bind(fdControl, (struct sockaddr*)&socketLocal, sizeof(struct sockaddr_in)) >= 0)
		listenControlSocket(fdControl);

	dbgprintf("%s-<\n", __FUNCTION__);
	return fdControl;
}

int checkControlSocket()
{
	dbgprintf("%s->\n", __FUNCTION__);
	int running = 0;

	struct sockaddr_in socketLocal;
	int fdControl = socket(PF_INET, SOCK_STREAM, 0);
	memset(&socketLocal, 0, sizeof(struct sockaddr_in));
	socketLocal.sin_family = AF_INET;
	socketLocal.sin_port = htons(CONTROL_PORT);
	socketLocal.sin_addr.s_addr = htonl(INADDR_ANY);

	if (bind(fdControl, (struct sockaddr*)&socketLocal, sizeof(struct sockaddr_in)) < 0)
		running = 1;

	close(fdControl);
	dbgprintf("%s-<, %d\n", __FUNCTION__, running);
	return running;

}

void * control (void * none)
{
	int fdControl = createControlSocket();
	//listenControlSocket(fdControl);
}

int checkForRunningInstance()
{
	return checkControlSocket();
}





int startDaemon()
{
	dbgprintf("%s->\n", __FUNCTION__);
	pid_t pid = fork();
	if (pid == 0)
	{
		openLogfile();
		printThis("starting daemon (%d)\n", pid);
		pthread_t answerUdpBroadcastThread;
		pthread_t tcpRequestsThread;
		pthread_t controlThread;
		int error = 0;

		error = pthread_create(&controlThread, NULL, control, NULL);
		if(error) printThis("Error while creating control Thread!\n");

		error = pthread_create(&answerUdpBroadcastThread, NULL, answerUdpBroadcast, NULL);
		if(error) printThis("Error while creating answerUdpBroadcast Thread!\n");

		error = pthread_create(&tcpRequestsThread, NULL, tcpRequests, NULL);
		if(error) printThis("Error while creating tcpRequests Thread!\n");

		//pthread_exit(NULL);
		while(!vShutdown)
		{
			usleep(200000);
		}
		closeLogfile();
	}
	dbgprintf("%s-<\n", __FUNCTION__);
	return 0;
}

int main(int argc, char**argv)
{
	fpLogfile = stdout;

	if(checkForRunningInstance() == 0)
	{
		startDaemon();
	} 
	else
	{
		//dbgprintf("%s argv: %s\n", __FUNCTION__, argv[1]);
		if (argc == 2 && !strncmp(argv[1], "log", 3))
		{
			int bufSize = 1024;
			char logfileName[1024];
			sendControlCommand(CONTROL_CMD_GETLOGFILENAME, logfileName, &bufSize);
			if(bufSize > 0) {
				logfileName[bufSize] = '\0';
				printf("LogfileName: %s\n", logfileName);
				FILE * fp = fopen(logfileName, "r");
				if (fp == NULL) perror ("Error opening file");
				char buf[1024];
				int lineNumber = 1;
				while(fgets (buf , 1024 , fp) > 0)
				{
					printf ("[%03d] %s", lineNumber++, buf);
				}
     				fclose (fp);
			}
		}
		else if (argc == 2 && !strncmp(argv[1], "stop", 4))
		{
			int bufSize = 0;
			sendControlCommand(CONTROL_CMD_SHUTDOWN, NULL, &bufSize);
		}
		else
			printf( "\nProcess is already running!\n"
				"\n"
				"Options are:\n"
				"\tlog         shows log\n"
				"\tstop        stop daemon\n"
				"\n");
	}
	return 0;
}

