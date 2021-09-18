# David Brown
# EEL4781
# Project 1
# 10/23/2020

''' client side '''
import socket
import json
import os
import sys 

# save file 
def client_save(filename, data):
    ''' '''
    # open the file for writing
    file = open(filename, 'a')
    
    # write data to file
    file_size = file.write(data)
    
    # return the file_size for error checking (should equal expected file size)
    return file_size

# read file 
def client_read(start_byte, end_byte, filename):
    ''' '''
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

# detect client responses (mostly errors)
def error_detection(msg):
    ''' '''
    # get the response from server
    response = msg.split(' ')[1]

    # byte range error
    if (response == ERROR_INVALID_BYTES):
        print('ERROR: Invalid byte range for ' + cmd['filename'] + ' requested on server.')
        return True
        
    # file requested doesnt exist error
    elif (response == ERROR_FILE_DNO):
        print('ERROR: Requested ' + cmd['filename'] + ' does not exist on server.')
        return True
        
    # file requested doesnt exist error
    elif (response == ERROR_FILE_EXISTS):
        print('ERROR: ' + cmd['filename'] + ' already exists on server.')
        return True

    # file requested doesnt exist error
    else:
        print('SUCCESS: ' + cmd['filename'] + ' was successfully written to server.')
        return False

# process user input for command
def process_input(cmd):
    ''' '''

    # catch errors in user input
    try:
        # initialize client header as dictionary -- default sends entire file to client
        client_header = {'client_name': '', 'server_name': '', 'filename': '', 'start_byte': 0, 'end_byte': 0, 'write_to_server': False}

        # split string
        client_msg = cmd.split(' ')
        client_header['client_name'] = client_msg[0] 
        client_header['server_name'] = client_msg[1] 
       
        # client wants to download byte range of file from server
        if (len(client_msg) == 7):
        
            client_header['filename'] = client_msg[2] 
            client_header['start_byte'] = int(client_msg[4])
            client_header['end_byte'] = int(client_msg[6])

            # incorrect flags for '-s' or '-e'
            if (client_msg[3] != '-s') or (client_msg[5] != '-e'):
                return {}

            # end_byte/start_byte are out of order (end byte < start byte)
            elif (client_header['end_byte'] < client_header['start_byte']):
                return {}

            # client cmd appears correct (client name, server name, filename, correct flags, )
            else:
                # return the command as a dictionary to send as json to server 
                return client_header

        # client wants to upload file to server
        elif (len(client_msg) == 4):
            client_header['write_to_server'] = True
            client_header['filename'] = client_msg[3] 
            
            # catch incorrect flag useage
            if (client_msg[2] != '[-w]'):
                return {}

            # command appears correct
            else:
                # return the command as a dictionary to send as json to server 
                return client_header

        # client wants to download entire file from server
        elif (len(client_msg) == 3):
            client_header['filename'] = client_msg[2] 

            # return the command as a dictionary to send as json to server 
            return client_header

        # error within input, return an empty dictionary and print usage()
        else:
            return {}

    # error catching, bad client input
    #   end_byte/start_byte are not integers 
    #   index out of range error
    except Exception as e:
        # catch any exceptions and print error msg
        print('Reading error: '.format(str(e)))
        return {}

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
            progress = "Sent {0}% of {1}".format(percent, filename)
            print(progress)
            return progress
    except:
        return 0 

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

# on client error, print help msg
def usage():
    ''''''
    help_msg = '''\n\n
    # File Server Usage Guide
    
    ## Download entire file from file server using following command:
    client_name server_name filename
    
    ## Download specific part of file from file server using following command and flags:
    client_name server_name filename -s START_BYTE -e END_BYTE 

    ## Upload entire file from file server using following command:
    client_name server_name [-w] filename

    ## Upload specific part of file from file server using following command and flags:
    client_name server_name [-w] filename -s START_BYTE -e END_BYTE 
    
    ## To quit file sharing program:
    quit\n\n
    '''
    print(help_msg)
    
# set constant header size
HEADER_SIZE = 256

# server responses (on successful write or some error)
ERROR_FILE_DNO = 'F_DNE' # file requested doesn't exist on server 
ERROR_INVALID_BYTES = 'INVALID_BYTE' # invalid byte range for file requested on server 
ERROR_FILE_EXISTS = 'F_EXISTS' # file being upload already exists on server 
SUCCESS_FILE_WRITE = 'F_WRITE' # file successfully written to server

# debug global variable
debug = 0

# debug
debug_mode(debug, 'DEBUG: client.py running...')

# create the socket
    # AF_INET == ipv4
    # SOCK_STREAM == TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to hostname @ port #
server_ip = 'net1547.net.ucf.edu' # hardcoded remote server ip 
PORT = 1234
s.connect((server_ip, PORT))

# debug
debug_mode(debug, 'DEBUG: client.py running...')

# keep connection open until receive message
while (True):

    # debug
    debug_mode(debug, 'DEBUG: client.py running HOST: {0} and PORT: {1}...'.format(server_ip, PORT))
    
    # initialize an empty string for complete_msg to send to server
    complete_msg = ''

    # initialize an empty string for tracking data from server
    server_msg = ''

    # set a bool when new_msg expected from server
    new_msg = True

    # get user input, process as cmd, and do not let user proceed until they quit or enter proper command
    is_cmd_invalid = True
    while (is_cmd_invalid):
        # get client command for server and process for header information (write, byte range, filename)
        args = input('Enter server command (\'quit\' to close connection): ')

        # quit the program
        if (args == 'quit'):
            # exit program
            sys.exit()

        # process input and put command into json header to send to server
        cmd = process_input(args)

        # incorrect command from user, print help, and have user re-enter commands
        if (len(cmd) == 0):
            usage()

        # break from loop since cmd is valid
        else:
            is_cmd_invalid = False
            break

    # convert cmd dictionary into string
    msg = json.dumps(cmd)

    # add the client command (msg json string) to buffered header 
    header = f"{msg:*<{HEADER_SIZE}}"# + msg#.encode('utf-8')

    # if trying to write, add body to header containing file to write from client
    if cmd['write_to_server'] == True: # write to file

        # error checking -- does file exist? if no, save and print:
        if (os.path.isfile(cmd['filename']) ):

            # get the data from client file 
            body = client_read(cmd['start_byte'], cmd['end_byte'], cmd['filename'])

            # add body to header
            complete_msg = header + body

        # else, file exists on client side, proceed
        else:
            print('Error: no file with filename ' + cmd['filename'] + ' exists.')

    # else, downloading file from server
    else:
        # set body equal to a blank string
        body = ''

        # add body to header
        complete_msg = header + body

    # send to server
    s.send(bytes(complete_msg, "utf-8"))


    # wait to receive message/file from server after client sends data
    while (True):
        # receive buffer of 16 (twice header_size) bytes of data from server, 1 byte == 1 char
        s_msg = s.recv(16) #
        msg = s_msg.decode("utf-8")

        # extract header telling client size of file in bytes
        # if receiving a new msg from server get the length of msg from header
        if (new_msg):
            
            # print length of message sent from server and save to var
            length_of_msg = int(msg.split(' ')[0])

            # error detection -- server sent error msg ('0 ERROR_TYPE/SUCCESS_TYPE')
            if (length_of_msg == 0):
                
                # get the response from server
                response = msg.split(' ')[1]
                
                # byte range error
                if (response == ERROR_INVALID_BYTES):
                    print('ERROR: Invalid byte range for ' + cmd['filename'] + ' requested on server.')
                    #break 
		            # exit program
                    sys.exit()
                   
                # file requested doesnt exist error
                elif (response == ERROR_FILE_DNO):
                    print('ERROR: Requested ' + cmd['filename'] + ' does not exist on server.')
                    #break 
		            # exit program
                    sys.exit()
                    
                # file requested doesnt exist error
                elif (response == ERROR_FILE_EXISTS):
                    print('ERROR: ' + cmd['filename'] + ' already exists on server.')
                    #break 
		            # exit program
                    sys.exit()

                # file requested doesnt exist error
                else:
                    #response == SUCCESS_FILE_WRITE
                    print('SUCCESS: ' + cmd['filename'] + ' was successfully written to server.')
                    #break 
		            # exit program
                    sys.exit()

            # new msg received so set bool to false
            new_msg = False

        # add the sent data to server_msg
        server_msg = server_msg + msg 
        
        #download progress of file download
        progress = download_progress(len(server_msg[HEADER_SIZE:]), length_of_msg, cmd['filename'])

        # message completely received 
        if len(server_msg) - HEADER_SIZE == length_of_msg:

            # reset the bool for new_msg since client has received full message
            new_msg = True
            
            # save (append) data to file
            size_of_file = client_save(cmd['filename'], server_msg[HEADER_SIZE:])

            # reset complete msg to empty string  
            complete_msg = ''

            # exit loop for new commands
            break

    # break out of outer loop, close connection, and end program
    break

# close connection with server
#s.close()
print('The client program has ended (re-run using shell command \'python3 client.py\'')

