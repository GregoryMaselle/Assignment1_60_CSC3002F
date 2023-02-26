import socket
import os
IP = socket.gethostbyname(socket.gethostname())
MSGFORMAT = "utf-8"
serverPort = 12000
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((IP, serverPort))
modifiedSentence = clientSocket.recv(1024)
print('From Server: ', modifiedSentence.decode())
inp = input('')
while len(inp) != 0:
    clientSocket.send(inp.encode(MSGFORMAT))
    if(inp == "X"):
      print(clientSocket.recv(1024).decode())
      file = inp('Please select a file to access')
      
     
clientSocket.close()