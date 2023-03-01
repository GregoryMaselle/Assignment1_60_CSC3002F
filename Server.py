import socket
import os
import hashlib
import sys

MSGFORMAT = "utf-8"
serverPort = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = socket.gethostbyname(socket.gethostname())
serverSocket.bind((IP, serverPort))

def findAndSend(reqFile,connectionSocket):
    passfail = 3;
    print("Hello World")
    os.chdir('./Database')
    password = 'abcdefg'
    pwords = open('passwords.txt','r')
    for line in pwords.readlines():
        lineList = line.split('/')   # Assuming we store as [filename]/[open or not]/[password]/[attempts]
        #for item in lineList:
            #print(item)
        target = lineList[0]
        if target == reqFile:
            if (lineList[1] == "open"):
                print(lineList[1])
                sendFile(reqFile, connectionSocket)
            else:
                passFail = 3
                passreq = "<PREQUEST>Please input password for "+reqFile
                connectionSocket.send(passreq.encode(MSGFORMAT))
                while (passFail > 0):
                    passSent = connectionSocket.recv(1024).decode()
                    print("\nHELLO THIS IS THE PASS SENT"+passSent)
                    if (passSent == lineList[2]):
                        successMessage = "<PACCEPT>Correct Password. Sending "+reqFile+"\n"
                        connectionSocket.send(successMessage.encode(MSGFORMAT))
                        sendFile(reqFile,connectionSocket)
                        break
                        
                    else:
                        #failureMessage = "<PREJECT>Password incorrect. You have " + str(passFail-1) + " attempts left.\n"
                        failureMessage = "<PREJECT>" + str(passFail-1)
                        
                        passFail = passFail - 1
                        connectionSocket.send(failureMessage.encode(MSGFORMAT))
                if (passfail == 0):
                    exitMessage = "You have exceeded the amount of attempts allowed to enter the password.\n"
                    print(exitMessage)
                    connectionSocket.send(exitMessage.encode(MSGFORMAT))
                    sys.exit(0)
                    
            if password == lineList[1]:
                #tell the user it was right or wrong
                #if wrong tell them theyre wrong, maybe add 1 to an attempt counter? 3rd part of file line?
                # if right -> ,
                    sendFile(reqFile, connectionSocket)
                    

def sendFile(reqFile,connectionSocket): # Sends filesize, bytes with a tagasd
   # try:##ss
    print("SENDING FILE")
    file = open(reqFile, 'rb')
    #filesize = os.path.getsize(reqFile)
    #connectionSocket.send(str(filesize).encode())
    data = file.read()
    print(data)
   # print(type(data))
    connectionSocket.sendall(data+b"<END>")
    #connectionSocket.send(b"<END>")
    file.close()
   # connectionSocket.send(hashlib.sha256(bytes(data)).hexdigest())a
    #except:    
    print("Successful")
    #connectionSocket.send("Fatal error in file transfer".encode(MSGFORMAT))

def main():
    path = './Database'
    isdir = os.path.isdir(path)
    if isdir is False:
        os.mkdir('./Database')
        os.chdir('./Database')
        f= open('passwords.txt','w')
        f.close()
        os.chdir('../')

    serverSocket.listen()
    print('The server is ready to receive')
    while True:
        connectionSocket, addr = serverSocket.accept()
        msg = "Client Connected; IP: "+addr[0]+"\n"+"Type X to access a file, type Y to upload a file."
        fileList = os.listdir("./Database")
   # prompt = "Type X to access a file, type Y to upload a file."
        connectionSocket.send(msg.encode(MSGFORMAT))
   # connectionSocket.send(prompt.encode(MSGFORMAT))
        ans = connectionSocket.recv(1024).decode()
        print(ans)
        if ans == "X":
            fileDisp = ""
            for filename in fileList:
                if filename == "passwords.txt":
                    continue
                fileDisp += filename + "\n"
            connectionSocket.send(fileDisp.encode(MSGFORMAT))
            reqFile = connectionSocket.recv(1024).decode()
            findAndSend(reqFile,connectionSocket)
           # connectionSocket.close()
        
    
if __name__ == '__main__':
    main()
