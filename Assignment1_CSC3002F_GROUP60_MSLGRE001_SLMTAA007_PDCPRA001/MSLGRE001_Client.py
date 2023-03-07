import socket #import socket library for server functionality
import os # import library to navigate through directories
import hashlib # import library to provide hashing functionality for data validation

MSGFORMAT = "utf-8"
IP = input("Enter IP: ")
serverPort = eval(input("Enter port number: "))
if (IP == "123"): # Used for testing purposes. Enables server and client to run on same machine.
  IP = socket.gethostbyname(socket.gethostname()) 
  serverPort = 9999


def receiveData(fileName, clientSocket):
  hashToCheck = hashlib.sha256() # create a hash that uses sha256
  clientDownloadPresent = os.path.isdir("./clientDownloads")
  if (clientDownloadPresent == False):
     os.mkdir("./clientDownloads")
  os.chdir("./clientDownloads")
  with open(fileName, "wb") as f:
    while True: 
      data = clientSocket.recv(4096) # receive the data
      #print(data)
      if data == b"<END>": # if the end tag has been spotted, stop writing.
        print("Test")
        break


      f.write(data[12:]) # write the data to the intended file.
      hashToCheck.update(data[12:]) # update the hash for every chunk of data.
      clientSocket.send("Data recieved".encode(MSGFORMAT))

  hashCode = clientSocket.recv(1024).decode()[12:] # receive the hash calulated by server.
  print(hashToCheck.hexdigest())
  if(hashToCheck.hexdigest() == hashCode): # if the hashes are equal, the file send was successful.
    clientSocket.send("<0><VLDDATA>Hashes are equal. Proceeding to download".encode(MSGFORMAT))
    print("Successful file download. Please reconnect to upload/download anything else.")
    clientSocket.close() # close the connection to server
    exit(1) # close the program

  else: # the hashes are UNEQUAL, the file send was a failure.
    clientSocket.send("<0><INVDATA>Hash mismatch. Please resend data.".encode(MSGFORMAT))
    print("Invalid data received. Reconnect and try again.")
    os.remove(fileName)# Delete the file that contains corrupted/invalid data received.
    clientSocket.close()# close the connection to server
    exit(1) # close the program



def clientDownloadControl(clientSocket,firstResp): # A method used to manage password and name input for downloads.
  print(firstResp[12:])
  fileName = input('Please select a file to access.\n')
  while(fileName == "passwords.txt"): # if the file requested is the password file, deny access, request another name.
     fileName = input('FILE INACCESSIBLE. CHOOSE A DIFFERENT FILE.')
  
  clientSocket.send(("<2><REQFILE>"+fileName).encode(MSGFORMAT))
  response = clientSocket.recv(1024).decode()

  while (response[3:12] == "<INVNAME>"): # if the name is invalid, ie the file is not on the server, ask client to try again.
     fileName = input("File not found. Please try again.\n")
     if(fileName == "abort"):
        clientSocket.close()
        exit(1)
     clientSocket.send(("<2><REQFILE>"+fileName).encode(MSGFORMAT))
     response = clientSocket.recv(1024).decode()

  if (response[3:12] == "<PREQUES>"): # the name is valid, request the password if file is not open.
    pAttempt = input("Please Enter The Password for "+fileName+"\n")
    clientSocket.send(("<2><PASSTRY>"+pAttempt).encode(MSGFORMAT))
    response = clientSocket.recv(1024).decode()

    while(response[3:12] == "<PREJECT>"): # while the password is invalid, keep requesting more password attempts.
      print(response[12:])
      pAttempt = input("")
      clientSocket.send(("<2><PASSTRY>"+pAttempt).encode(MSGFORMAT))
      response = clientSocket.recv(1024).decode()

    if(response[3:12]=="<PACCEPT>"): # The password has been accepted, keep progressing.
      receiveData(fileName, clientSocket)

    elif(response[3:12] == "<EXCPASS>"): # The Max number of password attempts has occured. The client will disconnect.
      print("Number of password attempts exceeded. Shutting connection.")
      clientSocket.close()

  else: 
    receiveData(fileName,clientSocket) # no password required, progress.
  
def clientUploadControl(clientSocket): # A method used to manage passwords and names for uploading files to server.
  print(clientSocket.recv(1024).decode()[12:])
  fileName = input('Please enter the file name\n') 

  while (fileName not in os.listdir("./")): # if the file does not exist in the same directory as Client.py, request different name or abort
     fileName = input('File not found. Try again or type "abort" to exit.\n')

     if(fileName == "abort"):
        clientSocket.close()
        exit(1)

  clientSocket.send(("<2><FILENAM>"+fileName).encode(MSGFORMAT))
  nameValidity = clientSocket.recv(1024).decode()

  while (nameValidity[3:12] == "<NMREJCT>"): # if the name is already in use, choose a different name or abort.
     fileName = input("File name not available. Choose another name or type 'abort' to exit. ")
     clientSocket.send(("<2><FILENAM>"+fileName).encode(MSGFORMAT))
     nameValidity = clientSocket.recv(1024).decode()
     
     if (fileName == "abort"):
        exit()
     
  print("File name received. Choose whether the file should be open or closed.")
  priv = input("Please enter file privacy. [open/closed]\n") # request privacy of file being uploaded.
  clientSocket.send(("<2><FILPRIV>"+priv).encode(MSGFORMAT))
  print(clientSocket.recv(1024).decode()[12:0])

  if (priv != "open"): # if the privacy chosen is 'closed' then invite the user to enter a password.
      password = input("Please enter a password for "+fileName+"\n")
      while(len(password) == 0):
         password = input("Please choose a password that is at least 1 character long.\n")
      clientSocket.send(("<2><PASSEND>"+password).encode(MSGFORMAT))
      print(clientSocket.recv(1024).decode()[12:0])
  
  hashToCheck = hashlib.sha256() # create a hash object that uses sha256 hashing.
  with open(fileName, "rb") as f: # open the target file on client machine.
      while True: 
          data = b"<2><FILDATA>"+f.read(4084) # read out a chunk of data from the desired file.
 
          if data == b"<2><FILDATA>": # when the end of file is reached, stop sending chunks.
              break
 
          clientSocket.sendall(data)# Send the chunk of data to the server.
          hashToCheck.update(data[12:])# Update the hash with new data.
          msg = clientSocket.recv(1024).decode(MSGFORMAT) 

      clientSocket.send(b"<END>") # Very important. Use identifier to indicate that the file has completed sending.
  clientSocket.send(("<2><HEXVALU>"+hashToCheck.hexdigest()).encode(MSGFORMAT))# Send the calculated hash to the server.

  response = clientSocket.recv(1024).decode()
  if(response[3:12] == "INVDATA"): # if the hash was a failure and the hashes do not match, close the connection and invite user to retry.
      print("File did not send successfully - hash codes not equal. Please reconnect and try again.")
      print(response[12:])
      clientSocket.close()
      exit(1)
  else:
      print("File sent successfully.") # The hash was a success and file was successfully uploaded.
      print(response[12:])
      clientSocket.close()
      exit(1)    



def main():
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket object
  try: 
    clientSocket.connect((IP, serverPort))
  except socket.error as e:
      print(str(e))
  prompt = clientSocket.recv(1024)  # Prompt from server inviting input from client.
  print('From Server: ', prompt.decode()[12:])
  inp = input('')
  
  while (inp != "Y" and inp != "X" and inp != "Q"): # while the input is valid, request valid input.
     inp = input("Invalid option. Please type 'X' to download, 'Y' to upload or 'Q' to quit\n")

  clientSocket.send(("<2><CLIRQST>"+inp).encode(MSGFORMAT))
  if(inp == "X"):# The client has chosen to download files.
    firstResp = clientSocket.recv(1024).decode()
    if(firstResp[3:12]=="<MPTYDTB>"):
       print(firstResp[12:])
       clientSocket.close()
       exit(1)
    clientDownloadControl(clientSocket,firstResp)

  elif (inp == "Y"): # the client has chosen to upload files.
    clientUploadControl(clientSocket)

  else:
    clientSocket.close() # the client has chosen to disconnect.
    exit(1)

if __name__ == "__main__":
   main()
