# File sharing server using python sockets
## Description
* This project is a simple file server which responds to client requests.
* Client can request to either read or write a file to server, either in it's entirety, or within a given byte range.
* As the file is being transferred between client/server, the percent of the file transferred is printed into the clientside terminal every second.
## How file server works
* Program was written in Python3 and therefore must be run using Python3 using the sys, os, json, and socket libraries.
* Command for running server (entered in remote server terminal, should run indefinitely):
	```bash
	python3 server.py
	```
* Command for running client (entered in client terminal):
	```bash
	python3 client.py
	```
* File transfer requests from client are sent to server and use the following general format: 
	```bash
	client_name server_name [-w] filename [-s] [start_byte] [-e] [end_byte]
	```
	* Client commands may contain the following flags;
		* The '[-w]' flag signifies client wants to write file to server
		* The '-s' START_BYTE flag, followed by integer representing first byte to get from file.
		* The '-e' END_BYTE flag, followed by integer representing last byte to get from file.
* Client user can enter 'help' command to receive a list of accepted commands, their format, and flags for each command:
```bash
help
```
* Client user can enter 'quit' to break the connection to server and terminate client-side program:
```bash
quit
```
* If client enters wrong flag or command, client side program recognizes this and prints a list of example commands.
* All other error handling is done by server, which sends client a response signifying their request triggered an error server side. The server responds with information regarding the given error (file does not exist client side or server side, invalid byte ranges, etc)
