import socket
import os
import hashlib
import sys


MSGFORMAT = "utf-8"
serverPort = 9999
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = socket.gethostbyname(socket.gethostname())# gets server IP address which is used to create the server socket for listening to connections.
print(IP)
# this try catch is used to catch any errors that occur with the socket being used to listen for connections.
try:
    serverSocket.bind((IP, serverPort))
except socket.error as e:
    print(str(e))


def findAndSend(reqFile,connectionSocket):#This method is run when a client tries to download a file from the server
    #passfail = 3;
    #print("Hello World")
    os.chdir('./Database') # enters the database directory where the files available for downloading by the client are stored.
    pwords = open('passwords.txt','r') # opens the passwords file used to check whether a requested file name exists in the database and whether it requires a password/ what the password is.
    valid = False
    while not valid:
        for line in pwords.readlines():
            lineList = line.split('/')   #Used to split each line of the passwords file into its file name, privacy and password.
            #for item in lineList:
                #print(item)
            target = lineList[0]
            #print(target)
            pword = lineList[2]
            #print(pword)
            if target == reqFile:#if the filename is located in the passwords file
                valid = True # checks 
                if (lineList[1] == "open"):#The file downloads if the file is not password protected
                    # if the file is opened, the user is informed of this and the server moves to start sending the file.
                    print(lineList[1])
                    connectionSocket.send("<0><NONPASS>NOPASSREQUIRED".encode(MSGFORMAT))
                    sendFile(reqFile, connectionSocket)#runs method to send the file to the client
                else:#if there is a password for the file
                    passFail = 3#the client has 3 tries to input the password
                    passreq = "<0><PREQUES>Please input password for "+reqFile
                    connectionSocket.send(passreq.encode(MSGFORMAT))#prompt to input password sent
                    while (passFail > 0):
                        passSent = connectionSocket.recv(1024).decode()[12:]#input received from client
                        #print("\nHELLO THIS IS THE PASS SENT"+passSent)
                    
                        if (str(passSent) == (pword)):#when the correct password is input
                            #print("Test correct")
                            successMessage = "<0><PACCEPT>Correct Password. Sending "+reqFile+"\n"
                            connectionSocket.send(successMessage.encode(MSGFORMAT))#notifies client that password is correct
                            sendFile(reqFile,connectionSocket)#sends file to client
                            break
                            
                        else:
                            #failureMessage = "<PREJECT>Password incorrect. You have " + str(passFail-1) + " attempts left.\n"
                            failureMessage = "<0><PREJECT>Password incorrect. You have " + str(passFail-1)+" attempts left.\n"#an error message is sent after an incorrect password attempt
                            
                            passFail = passFail - 1
                            connectionSocket.send(failureMessage.encode(MSGFORMAT))
                    print(str(passFail)+"PASSFAIL")
                # print(passfail == 0)
                    if (passFail == 0):#once the client fails the password input 3 times
                        exitMessage = "You have exceeded the amount of attempts allowed to enter the password.\n"#an error message is sent
                        print(exitMessage)
                        connectionSocket.send(("<1><EXCPASS>"+exitMessage).encode(MSGFORMAT))
                        connectionSocket.close()#and the socket is closed
        if (valid == False):#check in case the filename is not found in passwords.txt
            connectionSocket.send("<0><INVNAME>INVALIDNAME".encode(MSGFORMAT))
            print(reqFile + "THIS IS REQFILE")
            reqFile = connectionSocket.recv(1024).decode()[12:]

            pwords.seek(0)
                    

def sendFile(reqFile,connectionSocket): # Sends filesize, bytes with a tag
    #print("SENDING FILE")
    #file = open(reqFile, 'rb')
   # data = file.read()
    hValidation = hashlib.sha256()
    with open(reqFile, "rb") as f:#opens file and reads and sends file byte data a chunk at a time(if the file is big enough)
        while True:
            data = f.read(4096)
 
            if not data:#loops until no data is being sent
                break
 
            connectionSocket.sendall(data)
            hValidation.update(data)#hash is updated with new data
            #print("sending still")
            msg = connectionSocket.recv(1024).decode(MSGFORMAT)
        connectionSocket.send(b"<END>")#sends tag to show end of data
    connectionSocket.send(("<2><HEXVALU>"+hValidation.hexdigest()).encode(MSGFORMAT))
    response = connectionSocket.recv(1024).decode()
    if(response[3:12] == "INVDATA"):#error if hash of data does not match on either side
        print("File did not send successfully - hash codes not equal.")
        connectionSocket.close()
        os.chdir("../")
        return
    else:
        os.chdir("../")
        print("File sent successfully.")
        connectionSocket.close()#socket is closed after succesful file send
        return        
    
    #hValidation.digest()
    #print(hValidation.hexdigest())
   #     connectionSocket.sendall(("<2><HEXSEND>" + hValidation.hexdigest()).encode(MSGFORMAT))
   #     print(b"\n"+data)
   #     connectionSocket.sendall(b"<2><SFILSEN>"+data+b"<END>")
    #   connectionSocket.sendall(("<2><HEXSEND>"+hValidation.hexdigest()).encode(MSGFORMAT)+b"<2><SFILSEN>"+data+b"<END>")
    #file.close()



def recvFile(connectionSocket):#method ran when client is uploading a file to the server
    msg = "Ready to receive file - please send file name followed by the data."
    connectionSocket.send(("<0><RCVREDY>"+msg).encode(MSGFORMAT))
    passwordFile = open("./Database/passwords.txt")
    flag = True
    fName = ""
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

###################################33
    hValidation = hashlib.sha256()
    with open(fName, "wb") as f:
        while True:
            data = connectionSocket.recv(4096)

            if data == b"<END>":
            # print("\nDONE\n")
                break

            f.write(data)
            hValidation.update(data)
      #print(b"WRITING DATA "+data)
            connectionSocket.send("Data recieved".encode(MSGFORMAT))
    
    hashCode = connectionSocket.recv(1024).decode()[12:]
    print(hashCode)
    #connectionSocket.send(("<2><HEXVALU>"+hValidation.hexdigest()).encode(MSGFORMAT))
    #response = connectionSocket.recv(1024).decode()
    if(hValidation.hexdigest() == hashCode):
        print("Test")
        connectionSocket.send("<0><VLDDATA>The hash codes are equal and file has been uploaded - please reconnect if you would like to download/upload any more files.".encode(MSGFORMAT))
  #   file = open(fileName, "wb")
  #   file.write(fileBytes)
  #   file.close()
        print("File was uploaded successfully and hash codes matched.")
        connectionSocket.close()
        os.chdir("../")
        return
    else:
        connectionSocket.send("<0><INVDATA>The hash codes do not match. Please retransmit the data.".encode(MSGFORMAT))
  #   goFetch(fileName, clientSocket)
        print("Data received is invalid, connection has been closed and client has been prompted to try again.")
        os.remove(fName)
        connectionSocket.close()
        os.chdir("../")
        return
    # hashCode = connectionSocket.recv(1024).decode()[12:]
    # done = False
    # fileBytes = b""
    # #fileBytes = clientSocket.recv(1024)
    # byteData = connectionSocket.recv(1024)[12:]
    # while not done:
    #     #byteData = connectionSocket.recv(1024)
    #     #byteData = fileBytes
    #     if byteData[-5:] == b"<END>":
    #         fileBytes += byteData[:-5]
    #         print("Test")
    #        # print(byteData)
    #         #print(fileBytes)
    #         done = True
    #     else:
    #         #byteData = clientSocket.recv(1024)
    #         fileBytes += byteData
    #         byteData = connectionSocket.recv(1024)
        
        
    #     print(os.getcwd())
    #     #os.chdir("./Database")
        
    # hValidation = hashlib.sha256()
    # hValidation.update(fileBytes)
    # print(hValidation.hexdigest())
    # print(hashCode)
    # print(hValidation.hexdigest() == hashCode)
    # if(hValidation.hexdigest() == hashCode):
    #     file = open(fName, "wb")
    #     file.write(fileBytes)
    #     file.close()
    # else:
    #     connectionSocket.close()
    #     exit(1)

def main():#Main method ran on server start
    path = './Database'
    isdir = os.path.isdir(path)
    if isdir is False:#if there is no folder for the server files, a directory is made
        os.mkdir('./Database')
        os.chdir('./Database')
        f= open('passwords.txt','w')#a passwords file is kept here
        f.close()
        os.chdir('../')

    serverSocket.listen(2)#server waits for client
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
            for filename in fileList:#loop to display all of the files on the server, the passwords.txt file is hidden
                if filename == "passwords.txt":
                    continue
                fileDisp += filename + "\n"
            connectionSocket.send(fileDisp.encode(MSGFORMAT))#
            reqFile = connectionSocket.recv(1024).decode()[12:]
            findAndSend(reqFile,connectionSocket)#the file the client would like to download is used as a parameter
           # connectionSocket.close()
        elif ans == "Y":#If the client chooses to upload a file
            recvFile(connectionSocket)
        else:
            continue
        

        
        
    
if __name__ == '__main__':
    main()
