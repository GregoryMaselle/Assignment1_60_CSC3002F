import socket
import os

MSGFORMAT = "utf-8"
serverPort = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = socket.gethostbyname(socket.gethostname())
serverSocket.bind((IP, serverPort))

path = './Database'
isdir = os.path.isdir(path)
if isdir is False:
    os.mkdir('./Database')

serverSocket.listen()
print('The server is ready to receive')
while True:
    connectionSocket, addr = serverSocket.accept()
    msg = "Client Connected; IP: "+addr[0]+"\n"
    fileList = os.listdir("./Database")
    prompt = "Type X to access a file, type Y to upload a file."
    connectionSocket.send(msg.encode(MSGFORMAT))
    connectionSocket.send(prompt.encode(MSGFORMAT))
    ans = connectionSocket.recv(1024).decode()
    print(ans)
    if ans == "X":
        fileDisp = ""
        for filename in fileList:
            fileDisp += filename
        connectionSocket.send(fileDisp.encode(MSGFORMAT))
    #connectionSocket.close()
    #ADsdsada.sdfgh - password delimit by " ", check up until "." in file name to ensure full file name included.

