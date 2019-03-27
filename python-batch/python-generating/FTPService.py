from ftplib import FTP

class FTPService:

    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.ftpClient = None
        self.isConnected = False

    def login(self):
        try:
            self.ftpClient = FTP(self.host,self.username,self.password)
            self.isConnected = True
        except Exception as e:
            print(e)
            self.isConnected = False

    def list(self):
        if self.isConnected:
            print(self.ftpClient.nlst())

    def checkExistDirectory(self,dir):
        if dir in self.ftpClient.nlst():
            return True
        else:
            return False

    def createDirectory(self,dir):
        self.ftpClient.mkd(dir)

    def changeDirectory(self,path):
        if self.isConnected:
            try:
                self.ftpClient.cwd(path)
                return True
            except Exception as e:
                print(e)
                return False
        else:
            return False

    def uploadFile(self,remoteFileName, targetFile):
        if self.isConnected:
            try:
                self.ftpClient.storlines('STOR ' + remoteFileName, targetFile)
                return True
            except Exception as e:
                print(e)
                return False
        else:
            return False