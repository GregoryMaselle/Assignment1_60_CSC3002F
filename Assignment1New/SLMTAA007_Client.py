from socket import *
import os
import hashlib
import sys

# Client that can connect to a server to upload and download files 
# to/from the server.
# 01/03/23
# Done by Taahir Suleman - SLMTAA007

def recvFile(clientSocket, files):
  #files = clientSocket.recv(1024).decode()[12:] # receives list of files available for download from the server, converts it to a string excluding the message type details.
  print(files[12:]) # prints the file list
  fName = input('Please choose a file to download\n') # prompts user to select their desired file to download
  clientSocket.send(("<2><REQFILE>"+fName).encode()) # sends the file name to the server that the user would like to download
  msg = clientSocket.recv(1024).decode() # response from the server used to determine whether the file requested exists in the database and whether it requires a password.
  while (msg[3:12] == "<INVNAME>"):
    # if the file name is invalid (no file with that name exists in the database) the client will be prompted to enter a file name until they enter a valid one. 
     print(msg[12:])
     fName = input("")
     clientSocket.send(("<2><REQFILE>"+fName).encode())
     msg = clientSocket.recv(1024).decode()
  if (msg[3:12] == "<PREQUES>"):
    # used when the file requested requires a password.
    pAttempt = input("This file is protected. Please enter the password." + "\n")
    clientSocket.send(("<2><PASSTRY>"+pAttempt).encode()) # sends the password inputted by the user.
    msg = clientSocket.recv(1024).decode()
    while(msg[3:12] == "<PREJECT>"):
      # if the password entered is incorrect, the user is notified of this and prompted to enter a different password.
      pAttempt = input("The password entered is incorrect. Please try Again:\n")
      clientSocket.send(("<2><PASSTRY>"+pAttempt).encode())
      msg = clientSocket.recv(1024).decode()
      print(msg[12:])
    if(msg[3:12] == "<PACCEPT>"):
      # if the user enters the correct file, the client moves to begin downloading the file.
      print("Password entered is correct. File is being downloaded to current directory")
      downloadFile(fName, clientSocket)
    elif (msg[3:12] == "<EXCPASS>"):
      # if the user exceeds the maximum password attempts of 3, they are notified of this and the socket closes and application ends.
      print(msg[12:])
      clientSocket.close()
      exit(1)

  else: 
    # if the file is open, program immediately moves to begin downloading the file.
    print("File does not require a password and is being downloaded.")
    downloadFile(fName,clientSocket)


def downloadFile(fName, clientSocket):
  path = input("Please enter the file path to your desired download directory relative to the current directory.\n") # prompts the user to enter the desired directory which they want the file to be downloaded to
  os.chdir(path) # enters the directory in which the user wants to download the file to.
  
  file = open(fName, "wb") # opens a file in this directory to write the downloaded data to.
  done = False
  clientHash = hashlib.sha256() # initialises the hash code that is constantly updated as data is received and appended to the file.
  while not done:
    # this loop receives data in packets of 4096 bits, checks if it is the end tag and if not it appends the received data to the file and updates the hash code.
    byteData = clientSocket.recv(4096)
    if byteData == b"<END>":
      done = True
      file.close()
    else:
      file.write(byteData) # appends the received data to the file.
      clientHash.update(byteData) # updates the hash code to include the newly received data.
      clientSocket.send("Data packet received".encode())
      
  serverHash = clientSocket.recv(1024).decode()[12:] # receives and assigns the hash code derived on the server side to compare to hash code calculated by client and determine data validity.
  if("serverHash" == clientHash.hexdigest()):
    clientSocket.send("<0><VLDDATA>The hash codes match and the data is valid - file has been downloaded.".encode()) # informs the server that the hash codes match and the data received is valid.
    print("File has been downloaded and the connection will now close - please reconnect if you would like to upload/download any more files.") # informs the user that the connection will now close and the application will end.
    clientSocket.close() # closes the socket that was used for connecting to the server.
    exit(1) # exits the application.
  else:
    # if the hash codes do not match, the server and user is notified of this, the file is deleted on the client side and the connection and application is closed.
    clientSocket.send("<0><INVDATA>The hash code received does not match that calculated on the client side.".encode())
    print("Data received is invalid, please reconnect and try again.")
    os.remove(fName)
    clientSocket.close()
    exit(1)

def sendFile(clientSocket):
  print(clientSocket.recv(1024).decode()[12:]) 
  fName = input("Please enter file name.\n") # prompts the user to enter the file name of the file they would like to upload.
  if(fName not in os.listdir("./")): # checks whether the file the user would like to upload exists in the current directory.
    while True:
      fName = input('File does not exist in current directory. Please try  another file name or type "abort" to exit.\n')
      if(fName == "abort"):
        #closes connections and ends the application if user aborts.
        clientSocket.close()
        exit(1)
      if(fName in os.listdir("./")):
        # once the user enters a file name that does exist in their current 
        break
  clientSocket.send(("<2><FILENAM>"+fName).encode()) # once the file name is valid, it is sent to the server.
  response = clientSocket.recv(1024).decode() # used to check whether the file already exists in the database or not.
  while (response[3:12] == "<NMREJCT>"):
    # if the file name already exists in the database, the user is prompted to enter a different file name or to abort the process if they choose.
    print(response[12:])
    fName = input("")
    clientSocket.send(("<2><FILENAM>"+fName).encode())
    response = clientSocket.recv(1024).decode()
    
    if (fName == "abort"):
      # if the user chooses to abort, the connections closes and the application is exited.
      print("Exiting application.")
      clientSocket.close()
      exit(1)
  print(response[12:])
  priv = input("") # used to get the user's desired privacy choice.
  print(priv)
  clientSocket.send(("<2><FILPRIV>"+priv).encode())
  print(clientSocket.recv(1024).decode()[12:0])
  if (priv != "open"):
    print("Test")
    # if the user wants the file to be protected, they are asked to enter their desired password which is sent to the password.
    password = input("Please enter your desired password:\n")
    clientSocket.send(("<2><PASSEND>"+password).encode())
    print(clientSocket.recv(1024).decode()[12:0])
  clientHash = hashlib.sha256() # initialises the hash code to be constantly updated as the file is read and used to determine the reliability of the file upload to the server.
  file = open(fName, "rb")
  while True:
    byteData = file.read(4096) # reads 4096 bytes of data from the file at a time to be sent.
    if not byteData:
      # once we have reached the end of the file, the file is closed and the loop is exited.
      file.close()
      break
    clientSocket.sendall(byteData)
    clientHash.update(byteData) #iteratively updates the hash code as the data is read from the file.
    msg = clientSocket.recv(1024).decode()
  clientSocket.send(b"<END>") # after all the data has been sent, the end tag is sent to indicate the last bit has been sent.
  clientSocket.send(("<2><HEXVALU>"+clientHash.hexdigest()).encode()) # sends the hash code to tbe server for comparison.
  response = clientSocket.recv(1024).decode() # used to check whether the hash code matched the hash calculated on the server side
  if(response[3:12] == "<VLDDATA>"):
    # if the hashes match, user is notified, connection is closed and application is exited.
    print(response[12:])
    clientSocket.close()
    exit(1)
  else:
    # if the hashes do not match, user is notified, connection is closed and application is exited.
    print(response[12:])
    print("File upload unsuccessful.")
    clientSocket.close()
    exit(1)
    



        



def main():
  IP = sys.argv[1] # receives the server IP address as a command line argument from the user.
  serverPort = int(sys.argv[2]) # receives the server port number as a command line argument from the user.
  clientSocket = socket(AF_INET, SOCK_STREAM) # creates a TCP socket for connection to the server.
  clientSocket.connect((IP, serverPort)) # connects to the server using the specified server IP and port number.
  prompt = clientSocket.recv(1024).decode()[12:]
  print('From Server: ', prompt)
  inp = input('') #receives input from the client to indicate their desire to upload or download a file or quit the application.
  if (len(inp) != 0):
      clientSocket.send(("<2><CLIRQST>"+inp).encode()) # sends the user's response to server.
      if(inp == "X"):
        # if the input is X, this is sent to the server where it is first checked whether any files are available for download, if not, the connection is closed and application exited.
        response = clientSocket.recv(1024).decode()
        if(response[3:12] == "<MPTYDTB>"):
          print(response[12:])
          clientSocket.close()
          exit(1)
        recvFile(clientSocket, response) # if there are files available for download, the client can move to downloading a file.
      elif(inp == "Y"):
        # goes to the method used for uploading files.
        sendFile(clientSocket)
      else:
        # if any other input is received, connection is closed and application exited.
        clientSocket.close()
        exit(1)
  # if no input is received, connection is closed and application exited.
  clientSocket.close()
  exit(1)

if __name__ == "__main__":
   main()