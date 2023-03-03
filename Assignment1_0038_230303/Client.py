import socket
import os
import hashlib

MSGFORMAT = "utf-8"
IP = input("Enter IP: ")
serverPort = eval(input("Enter port number: "))
if (IP == "123"):
  IP = socket.gethostbyname(socket.gethostname())
  serverPort = 12000


def goFetch(fileName, clientSocket):
  print("gofetch run\n")
  done = False
  fileBytes = b""
  byteData = clientSocket.recv(1024)[12:]
  #print(byteData)
  while not done:
    #byteData = clientSocket.recv(1024)
    #byteData = fileBytes
    if byteData[-5:] == b"<END>":
      print("Test")
      done = True
      fileBytes += byteData[:-5]
      print(byteData)
      print(fileBytes)
    else:
      #byteData = clientSocket.recv(1024)
      fileBytes += byteData
      byteData = clientSocket.recv(1024)
      
      
    print("TEST")
    print(os.getcwd())
    os.chdir("./clientDownloads")
    hValidation = hashlib.sha256()
    hValidation.update(fileBytes)
    #hValidation.hexdigest()
    print(hValidation.hexdigest())
    file = open(fileName, "wb")
    file.write(fileBytes)
    file.close()



def fileFetch(clientSocket):
  print(os.getcwd())
  #os.chdir("./clientDownloads")
  print(clientSocket.recv(1024).decode()[12:])
  fileName = input('Please select a file to access\n')
  clientSocket.send(("<2><REQFILE>"+fileName).encode(MSGFORMAT))
  response = clientSocket.recv(1024).decode()
  print("RESPONSE BEFORE GOFETCH:"+response[3:12])
  if (response[3:12] == "<PREQUES>"):
    pAttempt = input("Please Enter Password for "+fileName+"\n")
    clientSocket.send(("<2><PASSTRY>"+pAttempt).encode(MSGFORMAT))
    response = clientSocket.recv(1024).decode()
    while(response[3:12] == "<PREJECT>"):
      pAttempt = input("Incorrect. Try Again:\n")
      clientSocket.send(("<2><PASSTRY>"+pAttempt).encode(MSGFORMAT))
      print(pAttempt)
      response = clientSocket.recv(1024).decode()
      print("\n"+response[0:12] + " response prefix")
    if(response[3:12]=="<PACCEPT>"):
      goFetch(fileName, clientSocket)

  else: 
    goFetch(fileName,clientSocket)
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

  
def fileSend(clientSocket):
  print(clientSocket.recv(1024).decode()[12:])
  fileName = input('Please enter the file name\n') 
  clientSocket.send(("<2><FILENAM>"+fileName).encode(MSGFORMAT))
  fileNameReply = clientSocket.recv(1024).decode()

  while (fileNameReply[3:12] == "<NMREJCT>"):
     print(fileNameReply)
     fileName = input("File name already in use. Choose a different name or 'abort'. ")
     clientSocket.send(("<2><FILENAM>"+fileName).encode(MSGFORMAT))
     fileNameReply = clientSocket.recv(1024).decode()
     
     if (fileName == "abort"):
        exit()
     
 # print(fileNameReply)
  print("File name received. Please specify whether the file should be open or protected.")
  priv = input("Please enter file privacy\n")
  clientSocket.send(("<2><FILPRIV>"+priv).encode(MSGFORMAT))
  print(clientSocket.recv(1024).decode()[12:0])
  if (priv != "open"):
      password = input("Please enter a password for "+fileName+"\n")
      clientSocket.send(("<2><PASSEND>"+password).encode(MSGFORMAT))
      print(clientSocket.recv(1024).decode()[12:0])
  
  file = open(fileName, 'rb')
    #filesize = os.path.getsize(reqFile)
    #connectionSocket.send(str(filesize).encode())
  data = file.read()
  #print(data)
  # print(type(data))
  clientSocket.sendall(b"<2><SFILSEN>"+data+b"<END>")
  #connectionSocket.send(b"<END>")
  file.close()


def main():
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  clientSocket.connect((IP, serverPort))
  prompt = clientSocket.recv(1024)
  print('From Server: ', prompt.decode()[12:])
  inp = input('')
  if len(inp) != 0:
      clientSocket.send(("<2><CLIRQST>"+inp).encode(MSGFORMAT))
      if(inp == "X"):
         #print("Test filefetch")
         fileFetch(clientSocket)
      else:
          fileSend(clientSocket)
      
  clientSocket.close()

if __name__ == "__main__":
   main()
