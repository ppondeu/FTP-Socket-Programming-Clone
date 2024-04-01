import socket
import time
import random
import getpass
import os

def calculate_transfer_rate(bytes_received, start_time, end_time):
    elapsed_time = (end_time - start_time) / 1e9
    bytes_received = bytes_received / 1024
    try:
        transfer_rate = bytes_received / elapsed_time
    except ZeroDivisionError:
        transfer_rate = 0
    return transfer_rate

def handlePathInput(s):
    s = s.strip()
    msg = ''
    for v in s:
        if v == ' ':
            break
        else:
            msg += v
    return msg
    
def sendAndRecieve(clientSocket, reqMsg):
            try:
                clientSocket.send(f"{reqMsg}\r\n".encode())
                res = clientSocket.recv(1024)
                return res
            except Exception as e:
                return None

def disconnect(clientSocket, mode):
    if (clientSocket):
            try:
                res = sendAndRecieve(clientSocket, "QUIT")
                print(res.decode().splitlines()[0])
                clientSocket.close()
                clientSocket = None
            except Exception as e:
                pass
    else:
        if mode == "DISCONNECT":
            print(f"Not connected.")

def authenticate(clientSocket, host):
     if clientSocket:
            try:
                username = input(f"User ({host}:(none)): ")
                reqMsg = f"USER {username}"
                res = sendAndRecieve(clientSocket, reqMsg)
                print(res.decode().splitlines()[0])

                if res.startswith(b"331"):
                    password = getpass.getpass(f"Password: ")
                    reqMsg = f"PASS {password}"
                    res = sendAndRecieve(clientSocket, reqMsg)
                    print(f"\n{res.decode().splitlines()[0]}")
                    if res.startswith(b"530"):
                        print("Login failed.")
                elif res.startswith(b"501"):
                    print("Login failed.")
                 
            except Exception as e:
                print("error", e)

def reqPort(clientSocket):
            ipV4 = clientSocket.getsockname()[0]
            localPort = random.randint(49152, 65534)
            
            reqMsg = f'PORT {",".join(ipV4.split("."))},{localPort>>8},{localPort & 0xFF}' 
            res = sendAndRecieve(clientSocket, reqMsg)

            return res, ipV4, localPort

def fileValidation(filename):
    try:
        with open(filename, 'wb') as file:
            pass

    except PermissionError as e:
        print(f"Error opening local file {filename}.\n> {filename}:Permission denied")
        return True

    except FileNotFoundError as e:
        print(f"Error opening local file {filename}.\n> {filename}:No such file or directory")
        return True

    return False
    
def sendPASV(clientSocket):
    res = sendAndRecieve(clientSocket, "PASV")
    if res == None:
        print("Connection closed by remote host.")
        clientSocket = None
        return None, None, True

    ipPort = res.decode()
    ipPort = ipPort[ipPort.find("(")+1:ipPort.find(")")]
    ipPort = ipPort.split(",")
    ipV4 = ".".join(ipPort[:4])
    localPort = int(ipPort[4]) * 256 + int(ipPort[5])

    return ipV4, localPort, False

def main():

    defaultPORT = 21
    port = defaultPORT
    host = None
    clientSocket = None
    isLocalhost = False

    while True:
        inp = input("ftp> ").strip()
        
        if len(inp) == 0:
            continue

        args = inp.split()
        command = args[0].lower()

        if command == "quit" or command == "bye":
            disconnect(clientSocket, "QUIT")
            break

        elif command == "disconnect" or command == "close":
            disconnect(clientSocket, "DISCONNECT")
            clientSocket = None
            isLocalhost = False
            pass

        elif command == "open":
            if clientSocket:
                print("Already connected to test.rebex.net, use disconnect first.")
                continue
            if len(args) == 1:
                openInput = input("To ").strip()
                if len(openInput) == 0:
                    print(f"Usage: open host name [port]")
                    continue

                openArgs = openInput.split()
                if len(openArgs) == 1:
                    port = defaultPORT
                else:
                    port = int(openArgs[1])

                host = openArgs[0]
            elif len(args) == 2:
                port = defaultPORT
                host = args[1]
            elif len(args) == 3:
                port = int(args[2])
                host = args[1]
            else:
                print(f"Usage: open host name [port]")
            try:
                # create connection
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientSocket.connect((host, port))
                print(f"Connected to {host}.")

                res = clientSocket.recv(1024)
                if res == None:
                    print("Not connected.")
                    continue
                for line in res.decode().splitlines():
                    print(line)
                    if "FileZilla Server 1.8.1" in line:
                        isLocalhost = True

                reqMsg = f"OPTS UTF8 ON"
                res = sendAndRecieve(clientSocket, reqMsg)
                print(res.decode().splitlines()[0])

                # user command
                authenticate(clientSocket, host)

            except socket.gaierror:
                print(f"Unknown host {host}.")
                clientSocket = None
            except Exception as e:
                print(f"Error: {e}")
        elif command == "user" or command == "u" or command == "us" or command == "use":
            if clientSocket == None:
                print("Not connected.")
                continue
            if len(args) == 1:
                username = input("Username ").strip()
                if len(username) == 0:
                    print("Usage: user username [password] [account]")
                    continue
                reqMsg = f"USER {username}"
                try:
                    res = sendAndRecieve(clientSocket, reqMsg)
                    if res == None:
                        print("Not connected.")
                        continue
                    print(res.decode().splitlines()[0])
                    if res.startswith(b"331"):

                        # password = input(f"Password: ")
                        password = getpass.getpass(f"Password: ")
                        reqMsg = f"PASS {password}"
                        res = sendAndRecieve(clientSocket, reqMsg)
                        print(f"\n{res.decode().splitlines()[0]}")
                        if res.startswith(b"530"):
                            print("Login failed.")
                    elif res.startswith(b"501"):
                        print("Login failed.")
                except Exception as e:
                    print("error", e)
                
            elif len(args) == 2:
                username = args[1]
                reqMsg = f"USER {username}"
                try:
                    res = sendAndRecieve(clientSocket, reqMsg)
                    if res == None:
                        print("Not connected.")
                        continue
                    print(res.decode().splitlines()[0])
                    if res.startswith(b"331"):
                        # password = input(f"Password: ")
                        password = getpass.getpass(f"Password: ")
                        reqMsg = f"PASS {password}"
                        res = sendAndRecieve(clientSocket, reqMsg)
                        print(f"\n{res.decode().splitlines()[0]}")
                        if res.startswith(b"530"):
                            print("Login failed.")
                    elif res.startswith(b"501") or res.startswith(b"530"):
                        print("Login failed.")
                except Exception as e:
                    print("error", e)

            elif len(args) == 3 or len(args) == 4:
                username = args[1]
                reqMsg = f"USER {username}"
                try:
                    res = sendAndRecieve(clientSocket, reqMsg)
                    if res == None:
                        print("Not connected.")
                        continue
                    print(res.decode().splitlines()[0])
                    if res.startswith(b"331"):
                        password = args[2]
                        reqMsg = f"PASS {password}"
                        res = sendAndRecieve(clientSocket, reqMsg)
                        print(f"{res.decode().splitlines()[0]}")
                        if res.startswith(b"530"):
                            print("Login failed.")
                    elif res.startswith(b"501") or res.startswith(b"530"):
                        print("Login failed.")
                except Exception as e:
                    pass
        elif command == "binary":
            if clientSocket == None:
                print("Not connected.")
                continue
            res = sendAndRecieve(clientSocket, "TYPE I")
            if res == None:
                print("Connection closed by remote host.")
                clientSocket = None
                continue
            print(res.decode().splitlines()[0])
        elif command == "ascii":
            if clientSocket == None:
                print("Not connected.")
                continue
            res = sendAndRecieve(clientSocket, "TYPE A")
            if res == None:
                print("Connection closed by remote host.")
                clientSocket = None
                continue
            print(res.decode().splitlines()[0])
        elif command == "pwd":
            if clientSocket == None:
                print("Not connected.")
                continue

            res = sendAndRecieve(clientSocket, "XPWD")
            if res == None:
                print("Connection closed by remote host.")
                clientSocket = None
                continue
            print(res.decode().splitlines()[0])
        elif command == "cd":
            if clientSocket == None:
                print("Not connected.")
                continue
            pathInput = ""
            cdInput = ""
            if len(args) == 1:
                cdInput = input("Remote directory ")
                if len(cdInput.strip()) == 0:
                    print("cd remote directory.")
                    continue
            elif len(args) > 1:
                cdInput = inp[2:]
            pathInput = handlePathInput(cdInput)
            reqMsg = f"CWD {pathInput}"
            res = sendAndRecieve(clientSocket, reqMsg)
            if res == None:
                print("Connection closed by remote host.")
                clientSocket = None
                continue
            print(res.decode().splitlines()[0])
        elif command == "rename":
            if clientSocket == None:
                print("Not connected.")
                continue
            remoteFile = ""
            toFile = ""
            if len(args) == 1:
                remoteFile = input("From name ")
                if len(remoteFile.strip()) == 0:
                    print("rename from-name to-name.")
                    continue
                toFile = input("To name ")
                if len(toFile.strip()) == 0:
                    print("rename from-name to-name.")
                    continue

            elif len(args) == 2:
                remoteFile = args[1]
                toFile = input("To name ")
                if len(toFile.strip()) == 0:
                    print("rename from-name to-name.")
                    continue
            elif len(args) > 2:
                remoteFile = args[1]
                toFile = args[2]
            
            reqMsg = f"RNFR {remoteFile}"
            res = sendAndRecieve(clientSocket, reqMsg)
            if res == None:
                print("Connection closed by remote host.")
                clientSocket = None
                continue

            print(res.decode().splitlines()[0])

            if res.startswith(b"350"):
                reqMsg = f"RNTO {toFile}"
                res = sendAndRecieve(clientSocket, reqMsg)
                if res == None:
                    print("Connection closed by remote host.")
                    clientSocket = None
                    continue
                print(res.decode().splitlines()[0])

        elif command == "delete":
            if clientSocket == None:
                print("Not connected.")
                continue
            remoteFile = ""
            if len(args) == 1:
                remoteFile = input("Remote file ")
                if len(remoteFile.strip()) == 0:
                    print("delete remote file.")
                    continue
            elif len(args) > 1:
                remoteFile = args[1]
            
            reqMsg = f"DELE {remoteFile}"
            res = sendAndRecieve(clientSocket, reqMsg)
            if res == None:
                print("Connection closed by remote host.")
                clientSocket = None
                continue
            print(res.decode().splitlines()[0])
        elif command == "ls":
            if not clientSocket:
                print("Not connected.")
                continue

            if len(args) > 3:
                print("Usage: ls remote directory local file.")
                continue
            
            res, ipV4, localPort = reqPort(clientSocket)
            
            if res == None:
                print("Connection closed by remote host.")
                clientSocket = None
                continue

            print(res.decode().splitlines()[0])

            if len(args) == 3:
                err = fileValidation(args[2])
                if err:
                    continue
  
            dataSocket = None
            conn = None

            if (res.startswith(b"200")):
                if isLocalhost:
                    ipV4, localPort, err = sendPASV(clientSocket)
                    
                    if err:
                        continue
                    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    dataSocket.connect((ipV4, localPort))

                    reqMsg = f"NLST" if len(args) == 1 else f"NLST {args[1]}"
                    res = sendAndRecieve(clientSocket, reqMsg)
                    print(res.decode().splitlines()[0])

                    if res.startswith(b"550") and len(args) == 3:
                        if os.path.exists(args[2]):
                            os.remove(args[2])
                        continue

                    if res.startswith(b"150"):
                        startTime = time.time_ns()
                        bytesReceived = 0
                        dataReceives = []
                        while True:
                            dataReceived = dataSocket.recv(1024)
                            bytesReceived += len(dataReceived)

                            if not dataReceived:
                                break
                            dataReceives.append(dataReceived)
                            if len(args) != 3:
                                print(dataReceived.decode(), end='')
                            
                        dataSocket.close()
                        endTime = time.time_ns()

                        if len(args) == 3:
                            with open(args[2], 'wb') as file:
                                for data in dataReceives:
                                    file.write(data)
                        
                        
                        res = clientSocket.recv(1024)
                        print(res.decode().splitlines()[0])
                    
                        transferRate = calculate_transfer_rate(bytesReceived, startTime, endTime)
                        print(f"ftp: {bytesReceived} bytes received in {(endTime - startTime)/1e9:.2f}Seconds {transferRate:.2f}Kbytes/sec.")
                    
                else:
                    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    dataSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    dataSocket.bind((ipV4, localPort))
                    dataSocket.listen(1)

                    conn, _ = dataSocket.accept()

                    reqMsg = f"NLST" if len(args) == 1 else f"NLST {args[1]}"
                    res = sendAndRecieve(clientSocket, reqMsg)
                    print(res.decode().splitlines()[0])

                    if res.startswith(b"550") and len(args) == 3:
                        if os.path.exists(args[2]):
                            os.remove(args[2])     
                        continue

                    if res.startswith(b"125"):
                        startTime = time.time_ns()
                        bytesReceived = 0
                        dataReceives = []
                        while True:
                            dataReceived = conn.recv(1024)
                            bytesReceived += len(dataReceived)

                            if not dataReceived:
                                break
                            dataReceives.append(dataReceived)
                            if len(args) != 3:
                                print(dataReceived.decode(), end='')
                        dataSocket.close()
                        conn.close()
                        endTime = time.time_ns()

                        if len(args) == 3:
                            with open(args[2], 'wb') as file:
                                for data in dataReceives:
                                    file.write(data)
                        
                        res = clientSocket.recv(1024)
                        print(res.decode().splitlines()[0])

                        transferRate = calculate_transfer_rate(bytesReceived, startTime, endTime)
                        print(f"ftp: {bytesReceived} bytes received in {(endTime - startTime)/1e9:.2f}Seconds {transferRate:.2f}Kbytes/sec.")
            elif res.startswith(b"550"):
                print("Connection closed by remote host.")
                clientSocket = None

        elif command == "get":
            if not clientSocket:
                print("Not connected.")
                continue
            remoteFile = ""
            localFile = ""
            if len(args) == 1:
                remoteFile = input("Remote file ")
                if len(remoteFile.strip()) == 0:
                    print("Remote file get [ local-file ].")
                    continue
                localFile = input("Local file ")
                if len(localFile.strip()) == 0:
                    localFile = remoteFile
            elif len(args) == 2:
                remoteFile = args[1]
                localFile = remoteFile
            elif len(args) >= 2:
                remoteFile = args[1]
                localFile = args[2]
            
            res, ipV4, localPort = reqPort(clientSocket)
            if res == None:
                print("Connection closed by remote host.")
                clientSocket = None
                continue

            print(res.decode().splitlines()[0])
            if res.startswith(b"200"):
                try:
                    if isLocalhost:
                        ipV4, localPort, err = sendPASV(clientSocket)
                        if err:
                            continue
                        dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        dataSocket.connect((ipV4, localPort))

                        reqMsg = f"RETR {remoteFile}"
                        res = sendAndRecieve(clientSocket, reqMsg)
                        print(res.decode().splitlines()[0])

                        if res.startswith(b"550"):
                            continue
                        if res.startswith(b"150"):
                            startTime = time.time_ns()
                            bytesReceived = 0
                            dataReceives = []
                            while True:
                                dataReceived = dataSocket.recv(1024)
                                bytesReceived += len(dataReceived)

                                if not dataReceived:
                                    break
                                dataReceives.append(dataReceived)

                            dataSocket.close()
                            endTime = time.time_ns()
                            try:
                                with open(localFile, 'wb') as file:
                                    for data in dataReceives:
                                        file.write(data)
                            except Exception as e:
                                print(f"Error opening local file /.\n> /:Unknown error number")
                            res = clientSocket.recv(1024)
                            print(res.decode().splitlines()[0])

                            transferRate = calculate_transfer_rate(bytesReceived, startTime, endTime)
                            print(f"ftp: {bytesReceived} bytes received in {(endTime - startTime)/1e9:.2f}Seconds {transferRate:.2f}Kbytes/sec.")
                    else:
                        dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        dataSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        dataSocket.bind((ipV4, localPort))
                        dataSocket.listen(1)

                        conn, _ = dataSocket.accept()

                        reqMsg = f"RETR {remoteFile}"
                        res = sendAndRecieve(clientSocket, reqMsg)
                        print(res.decode().splitlines()[0])

                        if res.startswith(b"550"):
                            continue

                        if res.startswith(b"125"):
                            startTime = time.time_ns()
                            bytesReceived = 0
                            dataReceives = []
                            while True:
                                dataReceived = conn.recv(1024)
                                bytesReceived += len(dataReceived)

                                if not dataReceived:
                                    break
                                dataReceives.append(dataReceived)
                            dataSocket.close()
                            conn.close()
                            endTime = time.time_ns()
                            try:
                                with open(localFile, 'wb') as file:
                                    for data in dataReceives:
                                        file.write(data)
                            except Exception as e:
                                print(f"Error opening local file /.\n> /:Unknown error number")
                            res = clientSocket.recv(1024)
                            print(res.decode().splitlines()[0])

                            transferRate = calculate_transfer_rate(bytesReceived, startTime, endTime)
                            print(f"ftp: {bytesReceived} bytes received in {(endTime - startTime)/1e9:.2f}Seconds {transferRate:.2f}Kbytes/sec.")

                except socket.gaierror:
                    print(f"Unknown host {host}.")
                    clientSocket = None
                except Exception as e:
                    print(f"Error opening local file /.\n> /:Unknown error number")

        elif command == "put":
            if not clientSocket:
                print("Not connected.")
                continue
            remoteFile = ""
            localFile = ""
            if len(args) == 1:
                localFile = input("Local file ")
                if len(localFile.strip()) == 0:
                    print("Local file put [ remote-file ].")
                    continue
                remoteFile = input("Remote file ")
                if len(remoteFile.strip()) == 0:
                    remoteFile = localFile
            elif len(args) == 2:
                localFile = args[1]
                remoteFile = localFile
            elif len(args) >= 2:
                localFile = args[1]
                remoteFile = args[2]
            
            # check if file exists
            try:
                with open(localFile, 'rb') as file:
                    pass
            except FileNotFoundError as e:
                print(f"{localFile}: File not found")
                continue
            except PermissionError as e:
                print(f"{localFile}: Permission denied")
                continue
            except Exception as e:
                print(f"{localFile}: Unknown error number")
                continue
            
            res, ipV4, localPort = reqPort(clientSocket)
            if res == None:
                print("Connection closed by remote host.")
                clientSocket = None
                continue

            print(res.decode().splitlines()[0])
            if res.startswith(b"200"):
                try:
                    if isLocalhost:
                        ipV4, localPort, err = sendPASV(clientSocket)
                        if err:
                            continue
                        reqMsg = f"STOR {remoteFile}"
                        res = sendAndRecieve(clientSocket, reqMsg)
                        print(res.decode().splitlines()[0])

                        dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        dataSocket.connect((ipV4, localPort))

                        if res.startswith(b"150"):
                            startTime = time.time_ns()
                            bytesReceived = 0
                            dataReceives = []
                            try:
                                with open(localFile, 'rb') as file:
                                    data = file.read(1024)
                                    while data:
                                        dataSocket.send(data)
                                        data = file.read(1024)
                                        bytesReceived += len(data)
                            except Exception as e:
                                print(f"Error opening local file /.\n> /:Unknown error number")
                                continue
                            dataSocket.close()
                            endTime = time.time_ns()
                            res = clientSocket.recv(1024)
                            print(res.decode().splitlines()[0])

                            transferRate = calculate_transfer_rate(bytesReceived, startTime, endTime)
                            print(f"ftp: {bytesReceived} bytes received in {(endTime - startTime)/1e9:.2f}Seconds {transferRate:.2f}Kbytes/sec.")
                    else:


                    
                        dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        dataSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        dataSocket.bind((ipV4, localPort))
                        dataSocket.listen(1)
                        dataSocket.settimeout(5)

                        conn, _ = dataSocket.accept()

                        reqMsg = f"STOR {remoteFile}"
                        res = sendAndRecieve(clientSocket, reqMsg)
                        print(res.decode().splitlines()[0])

                        if res.startswith(b"550"):
                            dataSocket.close()
                            conn.close()
                            continue

                except socket.gaierror:
                    print(f"Unknown host {host}.")
                    clientSocket = None
                except Exception as e:
                    continue
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()