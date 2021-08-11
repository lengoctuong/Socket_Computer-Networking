from socket import *
from threading import *
from tkinter.constants import COMMAND

clients = {}
passwords ={}
addrs = {}
IP = '127.0.0.1'    # IP = gethostbyname(gethostname())
PORT = 65432
LEN_QUEUE = 5
PACKET = 1024
ENCRYPT = 'utf-8'

def acceptConnections():
    while True:
        Connector, addr = Server.accept()
        addrs[Connector] = addr
        print('~~~~~ Connected with', addr)
        Thread(target=signIn, args=(Connector,)).start()

def signIn(Connector):
    try:
        while True:
            headerR = Connector.recv(PACKET).decode(ENCRYPT)
            if headerR == '1':
                name = Connector.recv(PACKET).decode(ENCRYPT)
                password = Connector.recv(PACKET).decode(ENCRYPT)
                '''Check name and password'''
                if True:
                    clients[Connector] = name
                    passwords[Connector] = password

                    Connector.sendall(bytes('1', ENCRYPT))
                    handleClient(Connector)
                    break
                else:
                    Connector.sendall(bytes('0', ENCRYPT))
            elif headerR == '2':
                signUp(Connector)
                break
            else:
                print(f'##### {addrs[Connector]} have disconnected!\n')
                del addrs[Connector]
                Connector.close()
                break
    except ConnectionResetError:
        print(f'##### {addrs[Connector]} have disconnected!\n')
        del addrs[Connector]
        Connector.close()

def signUp(Connector):
    try:
        while True:
            headerR = Connector.recv(PACKET).decode(ENCRYPT)
            if headerR == '1':
                name = Connector.recv(PACKET).decode(ENCRYPT)
                password = Connector.recv(PACKET).decode(ENCRYPT)
                '''Check name and password'''
                if True:
                    clients[Connector] = name
                    passwords[Connector] = password

                    Connector.sendall(bytes('1', ENCRYPT))
                    handleClient(Connector)
                    break
                else:
                    Connector.sendall(bytes('0', ENCRYPT))
            else:
                signIn(Connector)
                break
    except ConnectionResetError:
        print(f'##### {addrs[Connector]} have disconnected!\n')
        del addrs[Connector]
        Connector.close()

def handleClient(Connector):
    welcome = 'Welcome ' + str(addrs[Connector]) +'! If you want to exit, typing {quit}.'    # welcome = 'Welcome %s! If you want to exit, typing {quit}.' %clientName
    Connector.sendall(bytes(welcome, ENCRYPT))

    try:
        while True:
            try:
                msgR = Connector.recv(PACKET).decode(ENCRYPT)
                if msgR == '{quit}':
                    break        
                else:
                    Connector.sendall(bytes('This is answer', ENCRYPT))
            except ConnectionResetError:    # Handle error at line 33 when client close console after input client's name
                break
    finally:    # Handle other potential exceptions
        print(f'##### {addrs[Connector]} have disconnected!\n')
        del addrs[Connector]
        del clients[Connector]
        del passwords[Connector]
        Connector.close()

Server = socket(AF_INET, SOCK_STREAM)
Server.bind((IP, PORT))

Server.listen(LEN_QUEUE)
print('LISTENING...\n')
    
acceptThead = Thread(target=acceptConnections)
acceptThead.start()
acceptThead.join()

Server.close()