import socket
import os
IP = socket.gethostbyname(socket.gethostname())
MSGFORMAT = "utf-8"
serverPort = 12000
#rsas

def fileFetch(clientSocket):
  print(os.getcwd())
  #os.chdir("./clientDownloads")
  print(clientSocket.recv(1024).decode())
  fileName = input('Please select a file to access\n')
  clientSocket.send(fileName.encode(MSGFORMAT))
  fileSize = clientSocket.recv(1024).decode()
  done = False
  fileBytes = b""
  while not done:
    byteData = clientSocket.recv(1024)
    print(byteData)
    if byteData[-5:] == b"<END>":
      done = True
    else:
      fileBytes += byteData
  print("TEST")
  print(fileBytes)
  file = open(fileName, "wb")
  file.write(fileBytes)
  file.close()

  



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
