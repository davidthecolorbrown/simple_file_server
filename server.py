# David Brown
# EEL4781
# Project 1
# 10/23/2020

'''server side '''

import socket
import json
import os

# read file from server
def server_read(start_byte, end_byte, filename):
    ''' '''
    # get the size of file
    size = os.path.getsize(filename)

    # return error since requested byte range exceeds file size
    if (end_byte > size):
        return 0

    # open file
    file = open(filename)

    # read contents from file
    contents = file.read()

    # if no start_byte/end_byte specified by user, set default to copy whole file
    if (start_byte == 0) and (end_byte == 0):
        return contents

    # else return given range 
    data = contents[start_byte - 1:end_byte]
    return data

# save file 
def server_save(filename, data):
    ''' '''
    # open the file for writing
    file = open(filename, 'w')
    
    # write data to file
    file_size = file.write(data)
    
    # return the file_size for error checking (should equal expected file size)
    return file_size

# enable debug mode on server
def debug_mode(enabled, debug_msg):
    '''
    enabled == global int variable representing debug mode enabled
    # 1 -> print debug_msg
    # 0 -> do not print debug_msg
    
    # call debug function to print debug message in debug mode
    debug_mode(debug, "Test debug message")
    '''
    
    # if global debug variable is set to 1, print debug_msg
    if enabled == 1:
        print(debug_msg)

# print client progress towards downloading file
def download_progress(data_recv, file_size, filename):
    '''
    print client progress towards downloading file
    arg1: the current amt downloaded (bytes)
    arg2: the total size of file (bytes)
    arg3: filename for file being downloaded
    '''
    try:
        percent = round((data_recv / file_size) * 100)
       
        # ignore zero percent, since msg is sent in small chunks of bytes, and most of it at start is the header region
        if (percent == 0):
            return 0
        else:
            return percent
    except:
        return 0
   
# set constant header size
HEADER_SIZE = 256

# server responses (on successful write or some error)
ERROR_FILE_DNO = 'F_DNE' # file requested doesn't exist on server 
ERROR_INVALID_BYTES = 'INVALID_BYTE' # invalid byte range for file requested on server 
ERROR_FILE_EXISTS = 'F_EXISTS' # file being upload already exists on server 
SUCCESS_FILE_WRITE = 'F_WRITE' # file successfully written to server

# global debug variable (1 => print debug msg, 0 => do not print debug msg)
debug = 1

#debug_mode(debug, 'DEBUG: server.py running...')

# create the socket
# AF_INET == ipv4
# SOCK_STREAM == TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# REUSEADDR allows server socket to use reuse client address
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind (listen) to hostname at port #
PORT = 1234
s.bind((socket.gethostname(), PORT))

# server at socket can only deal with one connection
# allow queue of 10 connections
s.listen(10)
#s.listen(1)

# debug
#debug_mode(debug, 'DEBUG: connection to socket made...')

# listen for connection from a client... forever
while (True):
    # debug
    debug_mode(debug, 'DEBUG: listening to client connection at HOST: {0} and PORT: {1}...'.format(socket.gethostname(), PORT))

    # accept if client connects
    client, address = s.accept()
    debug_mode(debug, 'DEBUG: connection from {0} has been established....'.format(address))

    # connection with client made, continue
    while (True):

        # try to get client data, if connection lost, break out of loop
        try:

            # decode the message sent by client
            client_data = client.recv(1024)
            #debug_mode(debug, 'DEBUG: client_data received: {0}....'.format(client_data))

            # decode client msg
            msg = client_data.decode("utf-8")
            #debug_mode(debug, 'DEBUG: client_data decoded: {0}....'.format(msg))

            # parse message for header, body, removing buffer
            # get header data
            head = msg.split('*')[0]

            # get body data
            body = msg.split('*')[-1]

            # load the json string into python dictionary
            # catch any client-side input errors
            try: 
                cmd = json.loads(head)
            
            except:
                debug_mode(debug, 'User input error for cmd.')

                break
            
            # process user input message and return as a dictionary
            #debug_mode(debug, 'DEBUG: client_data processed for commands: {0}....'.format(cmd))
            
            # check whether client is attempting to write to server
            if (cmd['write_to_server'] == True):
                #debug_mode(debug, 'DEBUG: client is attempting to write to server, cmd[-w flag]: {0}....'.format(cmd['write_to_server']))
                
                # if file already exists, tell client writing to server not allowed
                if (os.path.isfile(cmd['filename'])):
                    error = '0 ' + ERROR_FILE_EXISTS
                    client.send(bytes(f"{error:<{HEADER_SIZE}}", "utf-8"))

                # else, file doesn't exist, client is free to write to server
                else:
                    file_size_saved = server_save(cmd['filename'], body)
                    success = '0 ' + SUCCESS_FILE_WRITE
                    client.send(bytes(f"{success:<{HEADER_SIZE}}", "utf-8"))
            
            #else, read from file of filename and give back to user
            else:

                # check if file exists on server side, if it does, proceed
                if (os.path.isfile(cmd['filename'])):
                    
                    # read file from server
                    file = server_read(start_byte=cmd['start_byte'], end_byte=cmd['end_byte'], filename=cmd['filename'])

                    # check if byte range exceeds size of file
                    if (file == 0):
                        #debug_mode(debug, 'DEBUG: byte range given by client exceeds size of file')
                        error = '0 ' + ERROR_INVALID_BYTES
                        client.send(bytes(f"{error:<{HEADER_SIZE}}", "utf-8"))

                    debug_mode(debug, 'DEBUG: Sending {0} file to {1} from start_byte={2} to end_byte={3} ....'.format(cmd['filename'], address, cmd['start_byte'], cmd['end_byte']))

                    # store the msg length as first part of message (header) 
                    # so client knows size of file
                    debug_mode(debug, 'DEBUG: server is sending file of size: {0}....'.format(len(file)))
                    file = f"{len(file):<{HEADER_SIZE}}"+file
                    #debug_mode(debug, 'DEBUG: server is sending file with data: {0}....'.format(file))
                    
                    # send data to connected client in chunks of 16 bytes
                    size = len(file)
                    bytes_per_send = 16

                    # send data in 16 byte chunks
                    for chunk in range(0, size, bytes_per_send):
                    
                        #download progress of file download
                        progress = download_progress(chunk, size, cmd['filename'])
                        debug_mode(debug, "Sent {0}% of {1}".format(progress, cmd['filename']))
                    
                        # send chunk to client
                        client.send(bytes(file[chunk : chunk + bytes_per_send], "utf-8"))

                    debug_mode(debug, "Sent 100% of {0}".format(cmd['filename']))

                    # send data to connected client
                    debug_mode(debug, "Finished sending {0} to {1}.".format(cmd['filename'], address))

                # else, file doesn't exist, 
                else:
                    debug_mode(debug, 'File does not exist on server')
                    error = '0 ' + ERROR_FILE_DNO
                    client.send(bytes(f"{error:<{HEADER_SIZE}}", "utf-8"))
        
        # close connection with client and restart listen
        except:
            break  
    
    # close connection with client
    client.close()
