from socket import *
from threading import *
from tkinter import *
from tkinter.messagebox import *
from time import *

IP = '127.0.0.1'    # IP = gethostbyname(gethostname())
PORT = 65432
PACKET = 1024
ENCRYPT = 'utf-8'

def receive():
    while 1:
        try:
            msgR = Client.recv(PACKET).decode(ENCRYPT)
            chatBoxObj.msgList.insert(END, msgR)
        except OSError:
            break

class SignIn(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title('Sign In')
        self.pack(fill=BOTH, expand=1)
        # self.style = Style()
        # self.style.theme_use('default')

        self.nameStr = StringVar()
        self.passwordStr = StringVar()
        self.name = Label(self, text = 'Name')
        self.name.place(x=40, y=20)
        self.password = Label(self, text = 'Password')
        self.password.place(x=40, y=50)
        self.nameEntry = Entry(self, textvariable=self.nameStr)
        self.nameEntry.focus()
        self.nameEntry.place(x=120, y=20)
        self.passwordEntry = Entry(self, textvariable=self.passwordStr)
        self.passwordEntry.place(x=120, y=50)

        self.logIn = Button(self, text='Log In', command=self.sendSignIn)
        self.logIn.place(x=120, y=80)
        self.msgSignUp = Label(self, text='You haven\'t account -> ')
        self.msgSignUp.place(x=140, y=110)
        self.signUp = Button(self, text='Sign Up', command=self.clickSignUp)
        self.signUp.place(x=270, y=110)
        self.parent.protocol('WM_DELETE_WINDOW', self.clickClose)

    def sendSignIn(self):
        name = self.nameStr.get()
        self.nameStr.set('')
        password = self.passwordStr.get()
        self.passwordStr.set('')

        if name == '' or password == '':
            showwarning('Warning', 'You don\'t input anything. Please input name and password!')
        else:
            header = '1'
            Client.sendall(bytes(header, ENCRYPT))
            sleep(0.5)
            Client.sendall(bytes(name, ENCRYPT))
            sleep(0.5)
            Client.sendall(bytes(password, ENCRYPT))

            if Client.recv(1024).decode(ENCRYPT) == '1':
                self.parent.destroy()
            else:
                showwarning('Warning', 'Name or password is incorrect. Try again!')

    def clickSignUp(self):
        header = '2'
        Client.sendall(bytes(header, ENCRYPT))
        
        signUp = Tk()
        signUpObj = SignUp(signUp)
        signUp.geometry('350x150+450+300')
        signUp.mainloop()

    def clickClose(self, event=None):
        check = askyesno('Quit', 'Do you want to exit?')
        if check == True:
            header = '3'
            Client.sendall(bytes(header, ENCRYPT))
            Client.close()
            self.parent.destroy()
            exit(0)

class SignUp(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title('Sign Up')
        self.pack(fill=BOTH, expand=1)
        # self.style = Style()
        # self.style.theme_use('default')

        self.nameStr = StringVar()
        self.passwordStr = StringVar()
        self.name = Label(self, text = 'Name')
        self.name.place(x=40, y=20)
        self.password = Label(self, text = 'Password')
        self.password.place(x=40, y=50)
        self.nameEntry = Entry(self, textvariable=self.nameStr)
        self.nameEntry.focus()
        self.nameEntry.place(x=120, y=20)
        self.passwordEntry = Entry(self, textvariable=self.passwordStr)
        self.passwordEntry.place(x=120, y=50)

        self.logIn = Button(self, text='Submit', command=self.sendSignUp)
        self.logIn.place(x=120, y=80)
        self.parent.protocol('WM_DELETE_WINDOW', self.clickClose)

    def sendSignUp(self):
        name = self.nameEntry.get()
        self.nameStr.set('')
        password = self.passwordEntry.get()
        self.passwordStr.set('')
        
        if name == '' or password == '':
            showwarning('Warning', 'You don\'t input anything. Please input name and password!')
        else:
            header = '1'
            Client.sendall(bytes(header, ENCRYPT))
            sleep(0.5)
            Client.sendall(bytes(name, ENCRYPT))
            sleep(0.5)
            Client.sendall(bytes(password, ENCRYPT))

            if Client.recv(1024).decode(ENCRYPT) == '1':
                signIn.destroy()
                self.parent.destroy()
            else:
                showwarning('Warning', 'Name have been used. Please choose other name!')

    def clickClose(self, event=None):
        if askyesno('Quit', 'Do you want to stop Sign Up?'):
            header = '2'
            Client.sendall(bytes(header, ENCRYPT))
            self.parent.destroy()

class ChatBox(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title('Instant Chat')
        self.pack(fill=BOTH, expand=1)
        # self.style = Style()
        # self.style.theme_use('default')

        self.frame1 = Frame(self)
        self.frame1.pack()
        self.frame2 = Frame(self)
        self.frame2.pack()

        self.scrollbar = Scrollbar(self.frame1)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.msgList = Listbox(self.frame1, width=70, height=30, yscrollcommand=self.scrollbar.set)
        self.msgList.pack(side=LEFT, fill=BOTH)

        self.msgS = StringVar()
        self.msgS.set('Input your request here! (Delete all to typing)')
        self.msgSEntry = Entry(self.frame2, width=60, textvariable=self.msgS)
        self.msgSEntry.focus()
        self.msgSEntry.bind('<Return>', self.sendChatBox)
        self.msgSEntry.grid(row=0, column=0)

        self.sendButton = Button(self.frame2, text='Send', command=self.sendChatBox)
        self.sendButton.grid(row=0, column=1)
        self.parent.protocol('WM_DELETE_WINDOW', self.clickClose)

    def sendChatBox(self, event=None):
        msg = self.msgS.get()
        self.msgS.set('')
        Client.sendall(bytes(msg, ENCRYPT))

        if msg == '{quit}':
            Client.close()
            self.parent.destroy()

    def clickClose(self, event=None):
        if askyesno('Quit', 'Do you want to exit?'):
            self.msgS.set('{quit}')
            self.sendChatBox()

signIn = Tk()
signInObj = SignIn(signIn)
signIn.geometry('350x150+400+250')

Client = socket(AF_INET, SOCK_STREAM)
Client.connect((IP, PORT))
signIn.mainloop()

chatBox = Tk()
chatBoxObj = ChatBox(chatBox)
chatBox.geometry('500x550')

receiveThread = Thread(target=receive)
receiveThread.start()
chatBox.mainloop()