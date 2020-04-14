from socket import *
import threading
import os

cookie = True

def response(clientSocket):
    request = clientSocket.recv(1024).decode()
    file = request.split(' ')
    print(request)
    fileName = file[1]

    if 'Cookie' in request:
        cookie=True
    else :
        cookie=False

    if fileName == "/" or fileName=="/index.html":
        fileName = "index.html"
        cookie=True;

    elif fileName == "/base.css":
        temp = fileName.split('/')
        fileName = temp[1]
        cookie=True;

    else:
        temp = fileName.split('/')
        fileName = temp[1]

    print ("'{}' file requested".format(fileName))


    file, status = open_file(fileName, cookie)
    clientSocket.send(get_header(fileName, status).encode())

    if status==200:
        clientSocket.send(file.read())
    elif status==403:
        clientSocket.send("403 Forbidden".encode())
    else:
        clientSocket.send("404 Not Found".encode())

    clientSocket.close()


def open_file(fileName, cookie):
    try:
        file = open(fileName, "rb")
        if cookie==False:
            return file, 403
        return file, 200
    except FileNotFoundError:
        return None, 404

def get_header(fileName, status):

    try:
        fileSize = os.path.getsize(fileName)
    except FileNotFoundError:
        fileSize = len("404 Not Found")

    if status == 200 :
        http = "HTTP/1.1 200 OK"
        length = "Content-Length: {}".format(fileSize)

        filetype = fileName.split('.')
        if filetype[1] == "html" :
            type = "Content-Type: text/html"
        elif filetype[1] == "css" :
            type = "Content-Type: text/css"
        else :
            type = "Content-Type: image/jpeg"

    elif status==404 :
        http = "HTTP/1.1 404 NON FOUND"
        type = "Content-Type: text/plain"
        length = "Content-Length: {}".format(fileSize)

    else :
        http = "HTTP/1.1 403 Forbidden"
        fileSize = len("403 Forbidden")
        type = "Content-Type: text/plain"
        length = "Content-Length: {}".format(fileSize)

    print("\r\n".join([http, type, length]) + "\r\n\r\n")
    return "\r\n".join([http, type, length]) + "\r\n\r\n"



serverPort = 10080
serverSocket = socket (AF_INET, SOCK_STREAM)

serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

serverSocket.bind(('', serverPort))
serverSocket.listen(5)

print( "Server is ready to receive. ")

while True:
    clientSocket, addr = serverSocket.accept()
    print("Connection from ", addr)

    t = threading.Thread(target=response, args=(clientSocket,))
    t.start()
