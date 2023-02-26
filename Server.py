import socket
import os
import hashlib

MSGFORMAT = "utf-8"
serverPort = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = socket.gethostbyname(socket.gethostname())
serverSocket.bind((IP, serverPort))

def findAndSend(reqFile,connectionSocket):
    os.chdir('./Database')
    password = 'abcdefg'
    pwords = open('passwords.txt','a')
    for line in pwords:
        lineList = line.split("/")   #Assuming we store as [filename]/[open or not]/[password]/[attempts]
        target = lineList[0]
        if target == reqFile:
            #REQUEST PASSWORD
            # if no password needed -> 
                send(reqFile)
            if password == lineList[1]:
                #tell the user it was right or wrong
                #if wrong tell them theyre wrong, maybe add 1 to an attempt counter? 3rd part of file line?
                # if right -> 
                    send(reqFile, connectionSocket)
                    

def send(reqFile,connectionSocket):
    file = open(reqFile, 'rb')
    filesize = os.path.getsize(reqFile)
    connectionSocket.send(str(filesize).encode())
    data = file.read()
    connectionSocket.sendAll(data)
    connectionSocket.send(b"<END>")
    connectionSocket.send(hashlib.sha256(data).hexdigest())

    

    



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
                fileDisp += filename
            connectionSocket.send(fileDisp.encode(MSGFORMAT))
            reqFile = connectionSocket.recv(1024).decode()
            findAndSend(reqFile,connectionSocket)
        
    #connectionSocket.close()
    #ADsdsada.sdfgh - password delimit by " ", check up until "." in file name to ensure full file name included.
if __name__ == '__main__':
    main()


