import socket #import socket library for server functionality
import os # import library to navigate through directories
import hashlib # import library to provide hashing functionality for data validation

MSGFORMAT = "utf-8"
IP = input("Enter IP: ")
serverPort = eval(input("Enter port number: "))
if (IP == "123"):
  IP = socket.gethostbyname(socket.gethostname()) 
  serverPort = 9999


def goFetch(fileName, clientSocket):
  print("gofetch run\n")
  done = False
  hValidation = hashlib.sha256()
  os.chdir("./clientDownloads")
  with open(fileName, "wb") as f:
    while True:
      data = clientSocket.recv(4096)

      if data == b"<END>":
       # print("\nDONE\n")
        break

      f.write(data)
      hValidation.update(data)
      #print(b"WRITING DATA "+data)
      clientSocket.send("Data recieved".encode(MSGFORMAT))
  hashCode = clientSocket.recv(1024).decode()[12:]
  if(hValidation.hexdigest() == hashCode):
    clientSocket.send("<0><VLDDATA>The hash codes are equal - file is being downloaded.".encode(MSGFORMAT))
  #   file = open(fileName, "wb")
  #   file.write(fileBytes)
  #   file.close()
    print("File is downloaded - please reconnect if you would like to download/upload any more files.")
    clientSocket.close()
    exit(1)
  else:
    clientSocket.send("<0><INVDATA>The hash codes do not match. Please retransmit the data.".encode(MSGFORMAT))
  #   goFetch(fileName, clientSocket)
    print("Data received is invalid, please reconnect and try again.")
    os.remove(fileName)
    clientSocket.close()
    exit(1)

  
  # hashCodePlusByte = clientSocket.recv(1024)
  # hashCode = hashCodePlusByte[12:hashCodePlusByte.index(b'<2><SFILSEN>')].decode()
  # print(hashCodePlusByte)
  # print(hashCode)
  # fileBytes = b""
  # #   byteData = clientSocket.recv(1024)[12:]
  # byteData = hashCodePlusByte[hashCodePlusByte.index(b'<2><SFILSEN>')+12:]
  # print(byteData)
  # while not done:
  #   #byteData = clientSocket.recv(1024)
  #   #byteData = fileBytes
  #   if byteData[-5:] == b"<END>":
  #     print("Test")
  #     done = True
  #     fileBytes += byteData[:-5]
  #     print(byteData)
  #     print(fileBytes)
  #   else:
  #     #byteData = clientSocket.recv(1024)
  #     fileBytes += byteData
  #     byteData = clientSocket.recv(1024)
      
      
  # print("TEST")
  # print(os.getcwd())
  # os.chdir("./clientDownloads")
  # hValidation = hashlib.sha256()
  # hValidation.update(fileBytes)
  # #hValidation.hexdigest()
  # print(hValidation.hexdigest() == hashCode)
  # if(hValidation.hexdigest() != hashCode):
  #   print("FATAL ERROR: FILE MISMATCH")
  #   clientSocket.close()
  #   exit(1)
  # file = open(fileName, "wb")
  # file.write(fileBytes)
  # file.close()



def fileFetch(clientSocket):
  print(os.getcwd())
  #os.chdir("./clientDownloads")
  print(clientSocket.recv(1024).decode()[12:])
  fileName = input('Please select a file to access\n')
  while(fileName == "password.txt"):
     fileName = input('INVALID FILENAME. PLEASE CHOOSE ANOTHER ONE')
  
  clientSocket.send(("<2><REQFILE>"+fileName).encode(MSGFORMAT))
  response = clientSocket.recv(1024).decode()
  print("RESPONSE BEFORE GOFETCH:"+response[3:12])

  while (response[3:12] == "<INVNAME>"):
     fileName = input("File not found. Choose another one\n")
     clientSocket.send(("<2><REQFILE>"+fileName).encode(MSGFORMAT))
     response = clientSocket.recv(1024).decode()

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
  
def fileSend(clientSocket):
  print(clientSocket.recv(1024).decode()[12:])
  fileName = input('Please enter the file name\n') 
  while (fileName not in os.listdir("./")):
     fileName = input('File not found. Try again or type "abort" to exit.\n')
     if(fileName == "abort"):
        clientSocket.close()
        exit(1)
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
  priv = input("Please enter file privacy, [open/closed]\n")
  clientSocket.send(("<2><FILPRIV>"+priv).encode(MSGFORMAT))
  print(clientSocket.recv(1024).decode()[12:0])
  if (priv != "open"):
      password = input("Please enter a password for "+fileName+"\n")
      clientSocket.send(("<2><PASSEND>"+password).encode(MSGFORMAT))
      print(clientSocket.recv(1024).decode()[12:0])
  
  hValidation = hashlib.sha256()
  with open(fileName, "rb") as f:
      while True:
          data = f.read(4096)
 
          if not data:
              break
 
          clientSocket.sendall(data)
          hValidation.update(data)
          #print("sending still")
          msg = clientSocket.recv(1024).decode(MSGFORMAT)
      clientSocket.send(b"<END>")
  clientSocket.send(("<2><HEXVALU>"+hValidation.hexdigest()).encode(MSGFORMAT))
  response = clientSocket.recv(1024).decode()
  if(response[3:12] == "INVDATA"):
      print("File did not send successfully - hash codes not equal. Please reconnect and try again.")
      print(response[12:])
      clientSocket.close()
      #os.chdir("../")
      exit(1)
  else:
      #os.chdir("../")
      print("File sent successfully.")
      print(response[12:])
      clientSocket.close()
      exit(1)    
  # file = open(fileName, 'rb')
  #   #filesize = os.path.getsize(reqFile)
  #   #connectionSocket.send(str(filesize).encode())
  # data = file.read()
  # hValidation = hashlib.sha256()
  # hValidation.update(data)
  # clientSocket.sendall(("<2><HEXSEND>" + hValidation.hexdigest()).encode(MSGFORMAT))
  # #print(data)
  # # print(type(data))
  # clientSocket.sendall(b"<2><SFILSEN>"+data+b"<END>")
  # #connectionSocket.send(b"<END>")
  # file.close()


def main():
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    clientSocket.connect((IP, serverPort))
  except socket.error as e:
      print(str(e))
  prompt = clientSocket.recv(1024)
  print('From Server: ', prompt.decode()[12:])
  inp = input('')
  
  while (inp != "Y" and inp != "X" and inp != "Q"):
     inp = input("Invalid option. Please select 'X' to download, 'Y' to upload or 'Q' to quit\n")
  clientSocket.send(("<2><CLIRQST>"+inp).encode(MSGFORMAT))
  if(inp == "X"):
    #print("Test filefetch")
    fileFetch(clientSocket)
  elif (inp == "Y"):
    fileSend(clientSocket)
  else:
    clientSocket.close()
    exit(1)

if __name__ == "__main__":
   main()
