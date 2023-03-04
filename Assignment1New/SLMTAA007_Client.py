from socket import *
import os
import hashlib
import sys

# Client that can connect to a server to upload and download files 
# to/from the server.
# 01/03/23
# Done by Taahir Suleman - SLMTAA007

def recvFile(clientSocket):
  files = clientSocket.recv(1024).decode()[12:] # receives list of files available for download from the server, converts it to a string excluding the message type details.
  print(files) # prints the file list
  fName = input('Please choose a file to download\n') # prompts user to select their desired file to download
  clientSocket.send(("<2><REQFILE>"+fName).encode()) # sends the file name to the server that the user would like to download
  msg = clientSocket.recv(1024).decode()
  if (msg[3:12] == "<PREQUES>"):
    print("Test preq")
    pAttempt = input("This file is protected. Please enter the password." + "\n")
    clientSocket.send(("<2><PASSTRY>"+pAttempt).encode())
    msg = clientSocket.recv(1024).decode()
    while(msg[3:12] == "<PREJECT>"):
      pAttempt = input("The password entered is incorrect. Please try Again:\n")
      clientSocket.send(("<2><PASSTRY>"+pAttempt).encode())
      #print(pAttempt)
      msg = clientSocket.recv(1024).decode()
      print(msg[12:])
    if(msg[3:12] == "<PACCEPT>"):
      print("test accept")
      #print("Password entered is correct. File is being downloaded to current directory")
      downloadFile(fName, clientSocket)

  else: 
    print("File does not require a password and is being downloaded.")
    downloadFile(fName,clientSocket)
    #done = False
    #fileBytes = b""
    #while not done:
      #byteData = clientSocket.recv(1024) 
      #if byteData[-5:] == b"<END>":
        #done = True
        #fileBytes += byteData[:-5]
        #print(byteData)
        #print(fileBytes)
      #else:
        #fileBytes += byteData
      
  #print("TEST")
  #os.chdir("./clientDownloads")
  #file = open(fileName, "wb")
  #file.write(fileBytes)
  #file.close()


def downloadFile(fName, clientSocket):
  print("In download file")
  serverHash = clientSocket.recv(1024).decode()[12:] # receives and assigns the hash code derived on the server side to compare to hash code calculated by client and determine data validity.
  done = False
  fileBytes = b""
  byteData = clientSocket.recv(1024)[12:]
  print(serverHash)
  while not done:
    print("in while")
    #byteData = clientSocket.recv(1024)
    #byteData = fileBytes
    print(byteData)
    if byteData[-5:] == b"<END>":
      print("TestIF")
      done = True
      fileBytes += byteData[:-5]
    else:
      fileBytes += byteData
      print(fileBytes)
      byteData = clientSocket.recv(1024)
      
    print("after while")
    #fileBytes = fileBytes[12:]
    clientHash = hashlib.sha256()
    clientHash.update(fileBytes)
    #if(clientHash.hexdigest() == serverHash):
    print("Test")
    file = open(fName, "wb")
    file.write(fileBytes)
    file.close()
    #else:
      #clientSocket.send("<0><INVFILE>Data received is invalid. Please retransmit.").encode()

def sendFile(clientSocket):
  print(clientSocket.recv(1024).decode()[12:])

def main():
  IP = sys.argv[1]
  serverPort = int(sys.argv[2])
  clientSocket = socket(AF_INET, SOCK_STREAM)
  clientSocket.connect((IP, serverPort))
  prompt = clientSocket.recv(1024)
  print('From Server: ', prompt.decode()[12:])
  inp = input('')
  if len(inp) != 0:
      clientSocket.send(("<2><CLIRQST>"+inp).encode())
      if(inp == "X"):
        recvFile(clientSocket)
      elif(inp == "Y"):
        sendFile(clientSocket)
      else:
        clientSocket.close()

if __name__ == "__main__":
   main()