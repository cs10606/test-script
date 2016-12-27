#encoding=utf8
import configparser,datetime,sys,os

#读取ini文件
def getIniFile(type,key):
    config=configparser.ConfigParser()
    # config.read_file(u"a.ini")
    # print(sys.path[0])
    config.read(sys.path[0]+os.path.sep+"config.ini",encoding="utf-8")
    return config[type][key]


def getTime(type):
    now = datetime.datetime.now()
    if type ==1:
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif type ==0:
        return now.strftime("%Y%m%d_%H%M%S")

def read_email(Memail):

    config = configparser.ConfigParser()
    config.read(sys.path[0]+os.path.sep+"config.ini", encoding='utf-8')
    # Memail.report = "report.xlsx"
    Memail.to_addr = eval(config['Email']['to_addr'])
    Memail.mail_host = config['Email']['mail_host']
    Memail.mail_user = config['Email']['mail_user']
    Memail.mail_pass =  config['Email']['mail_pass']
    Memail.port = config['Email']['port']
    Memail.headerMsg = config['Email']['headerMsg']
    return Memail



class logToFile():
    def __init__(self, logfile):
        self.logfile = logfile

    def record(self, msg):
        try:
            # msg=msg.encode('UTF-8')
            f=open(self.logfile,'a')
            print(msg)
            f.write('['+getTime(1)+'] '+msg+'\n')
            f.close()
        except IOError as e:
            print("open file "+self.logfile +" failed:"+e)

        except UnicodeEncodeError as e:
            print("write message  failed:" + e)
