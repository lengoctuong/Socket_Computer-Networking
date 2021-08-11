from socket import *
from threading import *
from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter import Frame
from time import *

lstProvinces = []
PORT = 65432
HEADER = 64
PACKET = 1024
FORMAT = 'utf-8'

def handlleExcConErr():
    showerror('ERROR', 'Have loss connected with Server. Application will be closed!')
    Client.close()
    exit(0)

def sendTwoTimes(msgS):
    msgSEn = msgS.encode(FORMAT)
    msgSEnLenEn = str(len(msgSEn)).encode(FORMAT)
    msgSEnLenEn += b' ' * (HEADER - len(msgSEnLenEn))
    Client.sendall(msgSEnLenEn)
    Client.sendall(msgSEn)

def receive(lstProvinces):
    while 1:
        try:
            msgRLen = Client.recv(HEADER).decode(FORMAT)
            headerR = Client.recv(int(msgRLen)).decode(FORMAT)

            if headerR == 'SendData':
                for i in range(63):
                    obj = []
                    for j in range(4):
                        msgRLen = Client.recv(HEADER).decode(FORMAT)
                        obj.append(Client.recv(int(msgRLen)).decode(FORMAT))

                    lstProvinces.append((obj[0], obj[1], obj[2], obj[3]))
            elif headerR == 'StopServer':
                showwarning('Disconnected', 'Server have stopped. Please close Application!')
                break
        except OSError:
            break

class InputIP(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title('Connect with Server')
        self.pack(fill=BOTH, expand=1)

        self.announce = Label(self, text='To connect with Server, you have to input IP of Server here!')
        self.announce.place(x=20, y=10)
        
        self.ipStr = StringVar()
        self.ip = Label(self, text='IP')
        self.ip.place(x=70, y=50)
        self.ipEntry = Entry(self, textvariable=self.ipStr)
        self.ipEntry.focus()
        self.ipEntry.bind('<Return>', self.clickConnect)
        self.ipEntry.place(x=100, y=50)

        self.ipButton = Button(self, text='Connect', command=self.clickConnect)
        self.ipButton.place(x=130, y=80)
        self.parent.protocol('WM_DELETE_WINDOW', self.clickClose)

    def clickConnect(self, event=None):
        global IP
        IP = self.ipStr.get()
        
        try:
            Client.connect((IP, PORT))
            self.parent.destroy()
        except OSError:
            showerror('ERROR', 'OS Error')
        except gaierror:
            showerror('ERROR', 'socket.gaierror')
        except ConnectionRefusedError:
            showwarning('Warning', 'Connection Refused Error')

    def clickClose(self):
        if askyesno('Quit', 'Do you want to exit?'):
            exit(0)

class SignIn(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title('Sign In')
        self.pack(fill=BOTH, expand=1)

        self.nameStr = StringVar()
        self.passwordStr = StringVar()

        self.name = Label(self, text='Name')
        self.name.place(x=40, y=20)
        self.password = Label(self, text='Password')
        self.password.place(x=40, y=50)

        self.nameEntry = Entry(self, textvariable=self.nameStr)
        self.nameEntry.focus()
        self.nameEntry.bind('<Return>', self.movePasswordEntry)
        self.nameEntry.place(x=120, y=20)
        self.passwordEntry = Entry(self, textvariable=self.passwordStr)
        self.passwordEntry.bind('<Return>', self.sendSignIn)
        self.passwordEntry.place(x=120, y=50)

        self.logIn = Button(self, text='Log In', command=self.sendSignIn)
        self.logIn.place(x=120, y=80)
        self.msgSignUp = Label(self, text='You haven\'t account -> ')
        self.msgSignUp.place(x=140, y=110)
        self.signUp = Button(self, text='Sign Up', command=self.clickSignUp)
        self.signUp.place(x=270, y=110)
        self.parent.protocol('WM_DELETE_WINDOW', self.clickClose)

    def movePasswordEntry(self, event=None):
        self.passwordEntry.focus()

    def sendSignIn(self, event=None):
        try:
            name = self.nameStr.get()
            password = self.passwordStr.get()

            if name == '' or password == '':
                showwarning('Warning', 'You don\'t input anything. Please input name and password!')
            else:
                header = 'SubmitAcc'
                sendTwoTimes(header)
                sendTwoTimes(name)
                sendTwoTimes(password)

                if Client.recv(1024).decode(FORMAT) == 'SuccessfulSignIn':
                    self.parent.destroy()
                else:
                    showwarning('Warning', 'Name or password is incorrect. Try again!')
        except ConnectionResetError:
            handlleExcConErr()

    def clickSignUp(self):
        try:
            header = 'SignUp'
            sendTwoTimes(header)
            
            signUp = Tk()
            signUpObj = SignUp(signUp)
            signUp.geometry('350x150+450+300')
            signUp.mainloop()
        except ConnectionResetError:
            handlleExcConErr()

    def clickClose(self, event=None):
        try:
            if askyesno('Quit', 'Do you want to exit?'):
                header = 'QuitClient'
                sendTwoTimes(header)

                Client.close()
                self.parent.destroy()
                exit(0)
        except ConnectionResetError:
            handlleExcConErr()

class SignUp(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title('Sign Up')
        self.pack(fill=BOTH, expand=1)

        self.nameStr = StringVar()
        self.passwordStr = StringVar()

        self.name = Label(self, text='Name')
        self.name.place(x=40, y=20)
        self.password = Label(self, text='Password')
        self.password.place(x=40, y=50)

        self.nameEntry = Entry(self, textvariable=self.nameStr)
        self.nameEntry.focus()
        self.nameEntry.bind('<Return>', self.movePasswordEntry)
        self.nameEntry.place(x=120, y=20)
        self.passwordEntry = Entry(self, textvariable=self.passwordStr)
        self.passwordEntry.bind('<Return>', self.sendSignUp)
        self.passwordEntry.place(x=120, y=50)

        self.logIn = Button(self, text='Submit', command=self.sendSignUp)
        self.logIn.place(x=120, y=80)
        self.parent.protocol('WM_DELETE_WINDOW', self.clickClose)

    def movePasswordEntry(self, event=None):
        self.passwordEntry.focus()

    def sendSignUp(self, event=None):
        try:
            name = self.nameEntry.get()
            password = self.passwordEntry.get()
            
            if name == '' or password == '':
                showwarning('Warning', 'You don\'t input anything. Please input name and password!')
            else:
                header = 'SubmitAcc'
                sendTwoTimes(header)
                sendTwoTimes(name)
                sendTwoTimes(password)

                if Client.recv(1024).decode(FORMAT) == 'SuccessfulSignUp':
                    signIn.destroy()
                    self.parent.destroy()
                else:
                    showwarning('Warning', 'Name have been used. Please choose other name!')
        except ConnectionResetError:
            handlleExcConErr()

    def clickClose(self):
        try:
            if askyesno('Quit', 'Do you want to stop Sign Up?'):
                header = 'QuitSignUp'
                sendTwoTimes(header)
                self.parent.destroy()
        except ConnectionResetError:
            handlleExcConErr()

class InfoWin(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background='lavender')
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title('Situation Covid-19 in VietNam')
        self.pack(fill=BOTH, expand=1)

        self.style = Style()
        self.style.theme_use("default")
        self.style.configure("Treeview", background="#D3D3D3", foreground="black", rowheight=20, fieldbackground="#D3D3D3")
        self.style.map('Treeview', background=[('selected', 'blue')])

        self.frame1 = Frame(self)
        self.frame1.pack()
        self.frame2 = Frame(self)
        self.frame2.pack()

        while len(lstProvinces) < 63:
            sleep(0.1)

        self.scroll = Scrollbar(self.frame1)
        self.scroll.pack(side=RIGHT, fill=Y)

        self.tree = Treeview(self.frame1, columns=(lstProvinces[0][0], lstProvinces[0][1], lstProvinces[0][2], lstProvinces[0][3]), height=25, yscrollcommand=self.scroll.set, selectmode='extended')
        self.scroll.config(command=self.tree.yview)
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='lightblue')

        self.tree.heading('#0', text='No.')
        self.tree.heading('#1', text=lstProvinces[0][0])
        self.tree.heading('#2', text=lstProvinces[0][1])
        self.tree.heading('#3', text=lstProvinces[0][2])
        self.tree.heading('#4', text=lstProvinces[0][3])

        self.tree.column('#0', stretch=YES, width=50)
        self.tree.column('#1', stretch=YES, width=150)
        self.tree.column('#2', stretch=YES, width=100, anchor=E)
        self.tree.column('#3', stretch=YES, width=100, anchor=E)
        self.tree.column('#4', stretch=YES, width=100, anchor=E)
        self.tree.pack(padx=20, pady=10)

        for i in range(1, 63):
            if i % 2 == 0:
                self.tree.insert(parent='', index='end', text=str(i), values=(lstProvinces[i][0], lstProvinces[i][1], lstProvinces[i][2], lstProvinces[i][3]), tags=('oddrow',))
            else: 
                self.tree.insert(parent='', index='end', text=str(i), values=(lstProvinces[i][0], lstProvinces[i][1], lstProvinces[i][2], lstProvinces[i][3]), tags=('evenrow',))

        self.refreshButton = Button(self.frame2, text='Refresh', command=self.clickRefresh)
        self.refreshButton.bind('<Return>', self.clickRefresh)
        self.refreshButton.grid(row=0, column=0, padx=10, pady=10)
        self.logOutButton = Button(self.frame2, text='Log Out', command=self.clickClose)
        self.logOutButton.grid(row=0, column=1, padx=10, pady=10)
        self.parent.protocol('WM_DELETE_WINDOW', self.clickClose)

    def clickRefresh(self, event=None):
        try:
            lstProvinces.clear()
            Client.sendall(bytes('RefreshData', FORMAT))

            for record in self.tree.get_children():
                self.tree.delete(record)
            
            while len(lstProvinces) < 63:
                sleep(0.1)

            for i in range(1, 63):
                if i % 2 == 0:
                    self.tree.insert(parent='', index='end', text=str(i), values=(lstProvinces[i][0], lstProvinces[i][1], lstProvinces[i][2], lstProvinces[i][3]), tags=('oddrow',))
                else: 
                    self.tree.insert(parent='', index='end', text=str(i), values=(lstProvinces[i][0], lstProvinces[i][1], lstProvinces[i][2], lstProvinces[i][3]), tags=('evenrow',))

            showinfo('Announcement', 'Have loaded the new data')
        except ConnectionResetError:
            handlleExcConErr()

    def clickClose(self):
        try:
            if askyesno('Quit', 'Do you want to exit?'):
                Client.sendall(bytes('QuitClient', FORMAT))
                Client.close()
                self.parent.destroy()
        except ConnectionResetError:
            handlleExcConErr()

Client = socket(AF_INET, SOCK_STREAM)

inputIP = Tk()
inputIPObj = InputIP(inputIP)
inputIP.geometry('350x150+400+150')
mainloop()

signIn = Tk()
signInObj = SignIn(signIn)
signIn.geometry('350x150+400+250')
signIn.mainloop()

receiveThread = Thread(target=receive, args=(lstProvinces, ))
receiveThread.start()

infoWin = Tk()
infoWinObj = InfoWin(infoWin)
infoWin.geometry('+400+50')
infoWin.mainloop()

Client.close()