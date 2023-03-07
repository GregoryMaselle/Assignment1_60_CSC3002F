import socket, os, hashlib

#Data required for formatting based on protocol
FORMAT = "utf-8"
NAMEREJ = "<NMREJCT>"
INVTAG = "<INVNAME>"
PREQTAG = "<PREQUES>"
PACCTAG = "<PACCEPT>"
VALHASHTAG = "<0><VLDDATA>"
INVDATATAG = "<0><INVDATA>"
INPPASTAG = "<2><PASSTRY>"
REQFILE = "<2><REQFILE>"
SENDFILETAG = "<2><FILENAM>"
PREJTAG = "<2><PREJECT>"
FPRIV = "<2><FILPRIV>"
PASSET = "<2><PASSEND>"
VALCHECK = "<2><HEXVALU>"
CHOICEREQ = "<2><CLIRQST>"

#User must enter IP and port
ip = socket.gethostbyname(socket.gethostname())
port = 10000
ip = input("Enter IP to connect: ")
port = eval(input("enter port number: "))

def uploadFile(cSock):#Method called when client wants to upload to server

	print(cSock.recv(1024).decode()[12:])
	fName = input("please enter a file to upload\n")#They must enter the file they would like to upload
	while (fName not in os.listdir("./")):
		fName = input("Can't find file. Enter another file name or 'Q' to quit:")#Error reached if the entered file can't be found
		if(fName == "Q"):
			cSock.close()
			exit(1)
	cSock.send((SENDFILETAG+fName).encode(FORMAT))
	serRes = cSock.recv(1024).decode()

	while(serRes[3:12] == NAMEREJ):#This triggers if a file with the input name is already on the server
		print(serRes)
		fName = input("File name already exists. Enter a different name or 'Q' to quit.")#error is shown and user is prompted to choose a different file or quit
		cSock.send((SENDFILETAG+fName).encode(FORMAT))
		serRes = cSock.recv(1024).decode()
		if(fName == "Q"):
			cSock.close()
			exit(1)
	privacy = input("File name valid. Should the file be open or closed\n")#User asked if they want the file to be password protected
	cSock.send((FPRIV+privacy).encode(FORMAT))
	print(cSock.recv(1024).decode()[12:0])
	if(privacy=="closed"):#If they do want password protection, they are prompted to enter a password
		pWord = input("Please enter a password for "+fName)
		cSock.send((PASSET+pWord).encode(FORMAT))
		print(cSock.recv(1024).decode()[12:0])

	hvalidation = hashlib.sha256()#Used to generate hash
	with open(fName, "rb") as f:#Sends file data to server piece by piece
		while True:
			fileData = b"<2><FILDATA>" +f.read(4084)

			if fileData == b"<2><FILDATA>":
				break

			cSock.sendall(fileData)
			hvalidation.update(fileData[12:])#Hash is updated with new data
			message = cSock.recv(1024).decode(FORMAT)
		cSock.send(b"<END>")#attatches tag to show the file data has all been sent
	cSock.send((VALCHECK+hvalidation.hexdigest()).encode(FORMAT))#Sends hash data to server
	res = cSock.recv(1024).decode()
	if(res[3:12] == "INVDATA"):#if there is a hash mismatch an error is thrown
		print("Hash mismatch, please reconnect and try again later.")
		print(res[12:])
		cSock.close()
		exit(1)
	else:#If the hashes are the same, the file is uploaded 
		print("File sent")
		print(res[12:])
		cSock.close()
		exit(1)

#Used when downloading a file, this method gets the data from the server and writes the file
def getFile(name, cSock):
	done = False
	hValidation = hashlib.sha256()
	os.chdir("./clientDownloads")
	with open(name, "wb") as f:
		while True:#Runs until the end of the file
			fileData = cSock.recv(4096)#A new piece of data is retreived from the server
			if fileData == b"<END>":#end condition
				break
			f.write(fileData[12:])#every piece of data got is written to the file on the client side
			hValidation.update(fileData[12:])#Hash is updated with current data
			cSock.send("Data received".encode(FORMAT))
		hashNum = cSock.recv(1024).decode()[12:]
		if(hValidation.hexdigest() == hashNum):#Checks if the hash of the data of the files match between client and server
			cSock.send((VALHASHTAG+"The hash numbers are equal, the file will be downloaded.").encode(FORMAT))
			print("File succesfully downloaded, please reconnect to perform further operations")
			cSock.close()
			exit(1)
		else:#error when hash mismatch occurs
			cSock.send((INVDATATAG+"The hash codes do not match. Please reprocess the data").encode(FORMAT))
			print("Data is invalid, the hash numbers have a mismatch, please reconnect and try again.")
			os.remove(name)
			cSock.close()
			exit(1)

def downloadFile(cSock):#Method used when client requests to download a file from the server
	print(cSock.recv(1024).decode()[12:])
	test = input("Please select a file to retreive.\n")#asks the client what file they want
	while(test == "password.txt"):#Does not let client access file passwords
		test = input("Invalid filename, please select a different file.")

	cSock.send((REQFILE+test).encode(FORMAT))#sends filename to server
	serRes = cSock.recv(1024).decode()
	
	while(serRes[3:12]==INVTAG):#if the file cant be found on the server, the client is prompted to enter another file name
		test = input("Can't find file, please choose a different file. Or enter 'Q' to quit.")
		if(test == "Q"):
			cSock.close()
			exit(1)
		cSock.send((REQFILE+test).encode(FORMAT))
		serRes = cSock.recv(1024).decode()
	if(serRes[3:12]== PREQTAG):#If the file needs a password, the client will be asked for the password
		inpPwrd = input("Enter password for: "+test+"\n")
		cSock.send((INPPASTAG+inpPwrd).encode(FORMAT))
		serRes = cSock.recv(1024).decode()
		while(serRes[3:12]==PREJTAG):#If they enter the wrong password, they will be notified and given their remaining attempts to get the password
			inpPwrd = input("Wrong password. Try again.\n")
			cSock.send((INPPASTAG+inpPwrd).encode(FORMAT))
			serRes = cSock.recv(1024).decode()
		if(serRes[3:12] == PACCTAG):#If the password is correct
			getFile(test, cSock)#This method is called to download the file
	else:
		getFile(test, cSock)#If the file has no password, it is downloaded






def main():
	cSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:#Sets up socket connection
		cSock.connect((ip, port))
	except socket.error as e:
		print(str(e))
	print("Server: "+cSock.recv(1024).decode()[12:])
	choice = input('')#Client must decide which function they would like to use
	while (choice!="Y" and choice!="X" and choice!="Q"):
		choice = input("Invalid choice. Select 'X' to download, 'Y' to upload, or 'Q' to quit\n")
	cSock.send((CHOICEREQ+choice).encode(FORMAT))
	if(choice == 'X'):#X to download from server
		downloadFile(cSock)
	elif(choice == 'Y'):#Y to upload to server
		uploadFile(cSock)
	elif(choice == "Q"):#Q quits program
		cSock.close()
		exit(1)

if __name__ == "__main__":
	main()
