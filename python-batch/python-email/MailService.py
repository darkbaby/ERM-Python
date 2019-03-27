import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE
from email.header import Header
from email.utils import formataddr

class MailService:

    def __init__(self):
        self.server = smtplib.SMTP('smtp.gmail.com',587)
        self.server.ehlo()
        self.server.starttls()
        self.msg = MIMEMultipart('alternative')

    def login(self,username,password):
        self.server.login(username,password)

    def setSender(self,senderEmail):
        self.sender = formataddr((str(Header(u'ERM_SEND_EMAIL', 'utf-8')), senderEmail))

    def setReceiver(self,receiverEmailList):
        self.receivers = receiverEmailList

    def setSubject(self,subject):
        self.subject = subject

    def setMessage(self,message):
        self.message = message

    def send(self):
        if not hasattr(self,'sender') or not hasattr(self,'receivers') or not hasattr(self,'message')\
                or not hasattr(self,'subject'):
            print('cant send email')
        else:
            self.msg['From'] = self.sender
            self.msg['To'] = COMMASPACE.join(self.receivers)
            self.msg['Subject'] = self.subject
            self.msg.attach(MIMEText(self.message,'html'))
            self.server.sendmail(self.sender, self.receivers, self.msg.as_string())

    def quit(self):
        self.server.quit()