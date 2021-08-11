from socket import *
from threading import *
from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter import Frame
import openpyxl

addrs = {}
lstAccs = []
lstProvinces =[]
linkAccs = 'Accounts.txt'
linkCoVN = 'CovidInVietNam.xlsx'

IP = gethostbyname(gethostname())
PORT = 65432
LEN_QUEUE = 5
HEADER = 64
PACKET = 1024
FORMAT = 'utf-8'

def readAccsFile():
    f = open(linkAccs, 'r')
    fileLst = f.readlines()

    for item in fileLst:
        acc = item.split('\t')
        name = acc[0]
        password = acc[1]
        lstAccs.append((name, password))

    f.close()

def readCoVNFile():
    e = openpyxl.load_workbook(linkCoVN)
    excel = e['VietNam']

    for i in range(1, 64):
        col1 = str(excel['A' + str(i)].value)
        col2 = str(excel['B' + str(i)].value)
        col3 = str(excel['C' + str(i)].value)
        col4 = str(excel['D' + str(i)].value)

        lstProvinces.append((col1, col2, col3, col4))

    e.close()

def sendTwoTimes(Connector, msgS):
    msgSEn = msgS.encode(FORMAT)
    msgSEnLenEn = str(len(msgSEn)).encode(FORMAT)
    msgSEnLenEn += b' ' * (HEADER - len(msgSEnLenEn))

    Connector.sendall(msgSEnLenEn)
    Connector.sendall(msgSEn)

def receiveTwoTimes(Connector):
    msgRLen = Connector.recv(HEADER).decode(FORMAT)
    msgR = Connector.recv(int(msgRLen)).decode(FORMAT)
    return msgR

def sendData(Connector):
    for i in range(63):
        for j in range(4):
            msgSEn = lstProvinces[i][j].encode(FORMAT)
            msgSEnLenEn = str(len(msgSEn)).encode(FORMAT)
            msgSEnLenEn += b' ' * (HEADER - len(msgSEnLenEn))

            Connector.sendall(msgSEnLenEn)
            Connector.sendall(msgSEn)

def addChildTree(Connector, type):
    global NoChild
    managerObj.tree.insert(parent='', index='end', id=NoChild, values=('', '', type))
    managerObj.tree.move(str(NoChild), str(addrs[Connector][1]), str(addrs[Connector][1]))
    NoChild += 1

def acceptConnections():
    global NoParent
    global NoChild
    NoParent = 1
    NoChild = 100

    try:
        while True:
            Connector, addr = Server.accept()
            addrs[Connector] = (addr, NoParent)
            managerObj.tree.insert(parent='', index='end', id=NoParent, text=str(NoParent), values=(addr[0], addr[1], 'Connected'))
            NoParent += 1

            Thread(target=signIn, args=(Connector,)).start()
    finally:
        exit(0)

def signIn(Connector):
    global NoChild
    try:
        while True:
            headerR = receiveTwoTimes(Connector)

            if headerR == 'SubmitAcc':
                name = receiveTwoTimes(Connector)
                password = receiveTwoTimes(Connector)

                if (name, password) in lstAccs:
                    addChildTree(Connector, 'Signed In')
                    Connector.sendall(bytes('SuccessfulSignIn', FORMAT))
                    handleClient(Connector)
                    break
                else:
                    Connector.sendall(bytes('FailedSignIn', FORMAT))
            elif headerR == 'SignUp':
                signUp(Connector)
                break
            elif headerR == 'QuitClient':
                addChildTree(Connector, 'Disconnected')
                del addrs[Connector]
                Connector.close()
                break
    except ConnectionResetError:
        addChildTree(Connector, 'Disconnected')
        del addrs[Connector]
        Connector.close()

def checkSignUp(name):
    for acc in lstAccs:
        if name == acc[0]:
            return False

    return True

def signUp(Connector):
    global NoChild
    try:
        while True:
            headerR = receiveTwoTimes(Connector)

            if headerR == 'SubmitAcc':
                name = receiveTwoTimes(Connector)
                password = receiveTwoTimes(Connector)

                if checkSignUp(name):
                    lstAccs.append((name, password))
                    writeAccsFile()
                    addChildTree(Connector, 'Signed Up')

                    Connector.sendall(bytes('SuccessfulSignUp', FORMAT))
                    handleClient(Connector)
                    break
                else:
                    Connector.sendall(bytes('FailedSignUp', FORMAT))
            elif headerR== 'QuitSignUp':
                signIn(Connector)
                break
    except ConnectionResetError:
        addChildTree(Connector, 'Disconnected')
        del addrs[Connector]
        Connector.close()

def handleClient(Connector):
    sendTwoTimes(Connector, 'SendData')
    sendData(Connector)
    addChildTree(Connector, 'Sent Data')

    try:
        while True:
            try:
                msgR = Connector.recv(PACKET).decode(FORMAT)
                if msgR == 'QuitClient':
                    break
                elif msgR == 'RefreshData':
                    lstProvinces.clear()
                    readCoVNFile()

                    sendTwoTimes(Connector, 'SendData')
                    sendData(Connector)
                    addChildTree(Connector, 'Refreshed Data')
            except ConnectionResetError:
                break
    finally:
        addChildTree(Connector, 'Disconnected')
        del addrs[Connector]
        Connector.close()

def writeAccsFile():
    f = open(linkAccs, 'w')
    for acc in lstAccs:
        f.write(acc[0] + '\t' + acc[1] + '\t' + '\n')
    
    f.close()

class Manager(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background='lavender')
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title('Manage Connection')
        self.pack(fill=BOTH, expand=1)

        self.style = Style()
        self.style.theme_use("default")
        self.style.configure("Treeview", background="#D3D3D3", foreground="black", rowheight=25, fieldbackground="#D3D3D3")

        self.frame1 = Frame(self)
        self.frame1.pack()
        self.frame2 = Frame(self)
        self.frame2.pack()

        self.scroll = Scrollbar(self.frame1)
        self.scroll.pack(side=RIGHT, fill=Y)

        self.tree = Treeview(self.frame1, columns=('Connected Clients', 'Port', 'Status'), height=20, yscrollcommand=self.scroll.set, selectmode='extended')
        self.scroll.config(command=self.tree.yview)

        self.tree.heading('#0', text='No.')
        self.tree.heading('#1', text='Connected Clients')
        self.tree.heading('#2', text='Port')
        self.tree.heading('#3', text='Status')

        self.tree.column('#0', stretch=YES, width=50)
        self.tree.column('#1', stretch=YES, width=300)
        self.tree.column('#2', stretch=YES, width=100)
        self.tree.column('#3', stretch=YES, width=200)
        self.tree.pack()

        self.stopButton = Button(self.frame2, text='Stop Server', command=self.clickClose)
        self.stopButton.pack(padx=10, pady=10)
        self.parent.protocol('WM_DELETE_WINDOW', self.clickClose)

    def clickClose(self):
        if askyesno('Stop Server', 'Do you want to stop Server?'):
            self.parent.destroy()

readAccsFile()
readCoVNFile()

Server = socket(AF_INET, SOCK_STREAM)
Server.bind((IP, PORT))
Server.listen(LEN_QUEUE)

acceptThead = Thread(target=acceptConnections)
acceptThead.start()

manager = Tk()
managerObj = Manager(manager)
manager.geometry('+300+50')
manager.mainloop()

for conn in addrs:
    sendTwoTimes(conn, 'StopServer')
    conn.close()

addrs.clear()
Server.close()