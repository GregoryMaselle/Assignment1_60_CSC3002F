import socket
import os
IP = socket.gethostbyname(socket.gethostname())
MSGFORMAT = "utf-8"
serverPort = 12000
#rsas

def goFetch(fileName, clientSocket):
  print("gofetch run\n")
  done = False
  fileBytes = b""
  #fileBytes = clientSocket.recv(1024)
  while not done:
    byteData = clientSocket.recv(1024)
    #byteData = fileBytes
    if byteData[-5:] == b"<END>":
      done = True
      fileBytes += byteData[:-5]
      print(byteData)
      print(fileBytes)
    else:
      #byteData = clientSocket.recv(1024)
      fileBytes += byteData
      
      
    print("TEST")
    print
    print(os.getcwd())
    os.chdir("./clientDownloads")
    file = open(fileName, "wb")
    file.write(fileBytes)
    file.close()



def fileFetch(clientSocket):
  print(os.getcwd())
  #os.chdir("./clientDownloads")
  print(clientSocket.recv(1024).decode())
  fileName = input('Please select a file to access\n')
  clientSocket.send(fileName.encode(MSGFORMAT))
  response = clientSocket.recv(1024).decode()
  if (response[0:10] == "<PREQUEST>"):
    pAttempt = input("Please Enter Password for "+fileName+"\n")
    clientSocket.send(pAttempt.encode(MSGFORMAT))
    response = clientSocket.recv(1024).decode()
    while(response[0:9] == "<PREJECT>"):
      pAttempt = input("Incorrect. Try Again:\n")
      clientSocket.send(pAttempt.encode(MSGFORMAT))
      response = clientSocket.recv(1024).decode()
      print("\n"+response[0:10] + " response prefix")
    if(response[0:9]=="<PACCEPT>"):
      goFetch(fileName, clientSocket)
      

     
  #fileSize = clientSocket.recv(1024).decode()
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

  



def main():
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  clientSocket.connect((IP, serverPort))
  prompt = clientSocket.recv(1024)
  print('From Server: ', prompt.decode())
  inp = input('')
  while len(inp) != 0:
      clientSocket.send(inp.encode(MSGFORMAT))
      if(inp == "X"):
         print("Test filefetch")
         fileFetch(clientSocket)
        
      
  clientSocket.close()

if __name__ == "__main__":
   main()
