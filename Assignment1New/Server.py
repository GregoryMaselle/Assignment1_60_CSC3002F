import socket
import os
import hashlib
import sys

MSGFORMAT = "utf-8"
serverPort = 9999
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = socket.gethostbyname(socket.gethostname())#gets server IP
print(IP)
serverSocket.bind((IP, serverPort))

def findAndSend(reqFile,connectionSocket):
    #passfail = 3;
    #print("Hello World")
    os.chdir('./Database')
    pwords = open('passwords.txt','r')
    valid = False
    while not valid:
        for line in pwords.readlines():
            lineList = line.split('/')   # Assuming we store as [filename]/[open or not]/[password]/[attempts]
            #for item in lineList:
                #print(item)
            target = lineList[0]
            print(target)
            pword = lineList[2]
            print(pword)
            if target == reqFile:
                valid = True
                if (lineList[1] == "open"):
                    print(lineList[1])
                    connectionSocket.send("<0><NONPASS>NOPASSREQUIRED".encode(MSGFORMAT))
                    sendFile(reqFile, connectionSocket)
                else:
                    passFail = 3
                    passreq = "<0><PREQUES>Please input password for "+reqFile
                    connectionSocket.send(passreq.encode(MSGFORMAT))
                    while (passFail > 0):
                        passSent = connectionSocket.recv(1024).decode()[12:]
                        print("\nHELLO THIS IS THE PASS SENT"+passSent)
                    
                        if (str(passSent) == (pword)):
                            #print("Test correct")
                            successMessage = "<0><PACCEPT>Correct Password. Sending "+reqFile+"\n"
                            connectionSocket.send(successMessage.encode(MSGFORMAT))
                            sendFile(reqFile,connectionSocket)
                            break
                            
                        else:
                            #failureMessage = "<PREJECT>Password incorrect. You have " + str(passFail-1) + " attempts left.\n"
                            failureMessage = "<0><PREJECT>Password incorrect. You have " + str(passFail-1)+" attempts left.\n"
                            
                            passFail = passFail - 1
                            connectionSocket.send(failureMessage.encode(MSGFORMAT))
                    print(str(passFail)+"PASSFAIL")
                # print(passfail == 0)
                    if (passFail == 0):
                        exitMessage = "You have exceeded the amount of attempts allowed to enter the password.\n"
                        print(exitMessage)
                        connectionSocket.send(("<1><EXCPASS>"+exitMessage).encode(MSGFORMAT))
                        connectionSocket.close()
        if (valid == False):
            connectionSocket.send("<0><INVNAME>INVALIDNAME".encode(MSGFORMAT))
            print(reqFile + "THIS IS REQFILE")
            reqFile = connectionSocket.recv(1024).decode()[12:]
            pwords.seek(0)
                    

def sendFile(reqFile,connectionSocket): # Sends filesize, bytes with a tagasd
    print("SENDING FILE")
    file = open(reqFile, 'rb')
    data = file.read()
    hValidation = hashlib.sha256()
    hValidation.update(data)
    #hValidation.digest()
    #print(hValidation.hexdigest())
   #     connectionSocket.sendall(("<2><HEXSEND>" + hValidation.hexdigest()).encode(MSGFORMAT))
   #     print(b"\n"+data)
   #     connectionSocket.sendall(b"<2><SFILSEN>"+data+b"<END>")
    connectionSocket.send(("<2><HEXSEND>"+hValidation.hexdigest()).encode(MSGFORMAT)+b"<2><SFILSEN>"+data+b"<END>")
    file.close()
    os.chdir("../")
    print("Successful")


def recvFile(connectionSocket):
    msg = "Ready to receive file - please send file name followed by the data."
    connectionSocket.send(("<0><RCVREDY>"+msg).encode(MSGFORMAT))
    passwordFile = open("./Database/passwords.txt")
    flag = True
    while flag: 
        flag = False
        fName = connectionSocket.recv(1024).decode()[12:]
        print("FNAME IS THIS: "+fName)
        if (fName == "abort"):
            connectionSocket.shutdown(socket.SHUT_RDWR)
            connectionSocket.close()
            return
        for line in passwordFile:
            print(line)
            if (fName == line.split("/")[0]):
                msg = "<0><NMREJCT>This filename already exists. Choose another one or type 'abort' to exit."
                connectionSocket.send(msg.encode(MSGFORMAT))
                flag = True
        passwordFile.seek(0)
        print(flag)
        
    #print(msg)
    msg = "<0><NMSCCSS>File name received. Please specify whether the file should be open or protected."
    connectionSocket.send(msg.encode(MSGFORMAT))
    priv = connectionSocket.recv(1024).decode()[12:]
    if (priv == "open"):
        msg = "Privacy received. Please send the file in byte form."
        connectionSocket.send(("<1><PRIVREC>"+msg).encode(MSGFORMAT))
        os.chdir("./Database")
        file = open("passwords.txt", 'a')
        file.write(fName + "/" + priv + "/" + "a/" + "\n")
    else:
        msg = "Privacy received. Please send the desired password."
        connectionSocket.send(("<0><PASSREQ>"+msg).encode(MSGFORMAT))
        pWord = connectionSocket.recv(1024).decode()[12:]
        msg = "Password received. Please send the file in byte form."
        connectionSocket.send(msg.encode(MSGFORMAT))
        os.chdir("./Database")
        file = open("passwords.txt", 'a')
        file.write(fName + "/" + priv + "/" + pWord + "/" + "\n")

    hashCode = connectionSocket.recv(1024).decode()[12:]
    done = False
    fileBytes = b""
    #fileBytes = clientSocket.recv(1024)
    byteData = connectionSocket.recv(1024)[12:]
    while not done:
        #byteData = connectionSocket.recv(1024)
        #byteData = fileBytes
        if byteData[-5:] == b"<END>":
            fileBytes += byteData[:-5]
            print("Test")
           # print(byteData)
            #print(fileBytes)
            done = True
        else:
            #byteData = clientSocket.recv(1024)
            fileBytes += byteData
            byteData = connectionSocket.recv(1024)
        
        
        print(os.getcwd())
        #os.chdir("./Database")
        
    hValidation = hashlib.sha256()
    hValidation.update(fileBytes)
    print(hValidation.hexdigest())
    print(hashCode)
    print(hValidation.hexdigest() == hashCode)
    if(hValidation.hexdigest() == hashCode):
        file = open(fName, "wb")
        file.write(fileBytes)
        file.close()
    else:
        connectionSocket.close()
        exit(1)

def main():#Main method ran on server start
    path = './Database'
    isdir = os.path.isdir(path)
    if isdir is False:#if there is no folder for the server files, a directory is made
        os.mkdir('./Database')
        os.chdir('./Database')
        f= open('passwords.txt','w')#a passwords file is kept here
        f.close()
        os.chdir('../')

    serverSocket.listen()#server waits for client
    print('The server is ready to receive')
    while True:
        connectionSocket, addr = serverSocket.accept()
        msg = "<0><CONNSCS>Client Connected; IP: "+addr[0]+"\n"+"Type X to access a file, type Y to upload a file or, type Q to quit."
        fileList = os.listdir("./Database")
   # prompt = "Type X to access a file, type Y to upload a file."
        connectionSocket.send(msg.encode(MSGFORMAT))
   # connectionSocket.send(prompt.encode(MSGFORMAT))
        ans = connectionSocket.recv(1024).decode()[12:]
        print(ans)
        if ans == "X":#If the client chooses to download a file
            fileDisp = "<2><LISTFIL>"
            for filename in fileList:
                if filename == "passwords.txt":#The client is not allowed to download the password file
                    continue
                fileDisp += filename + "\n"
            connectionSocket.send(fileDisp.encode(MSGFORMAT))
            reqFile = connectionSocket.recv(1024).decode()[12:]
            findAndSend(reqFile,connectionSocket)
           # connectionSocket.close()
        elif ans == "Y":
            recvFile(connectionSocket)
        

        
        
    
if __name__ == '__main__':
    main()