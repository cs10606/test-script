#!/usr/local/python
#coding=utf-8

import os
from os import sys
import sys,time
import datetime
import smtplib
#import email
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.utils import COMMASPACE,formatdate
from email import Encoders
import ConfigParser,commands

#emailSender= 'sy5259@163.com'
#emailPassword='@sy5259'
emailSender= 'johnsonshi@dengtacj.com'
emailPassword="dengtacj@20151"
#emailRe1= ["johnsonshi@dengtacj.com","bgirlyang@dengtacj.com","xuebinliu@dengtacj.com","davidwei@dengtacj.com","steve@dengtacj.com"]
#emailRe1= ['johnsonshi@dengtacj.com']
#emailRe2= ['johnsonshi@dengtacj.com','bgirlyang@dengtacj.com','xuebinliu@dengtacj.com','waynettwan@dengtacj.com','kevintian@dengtacj.com','rincocheng@dengtacj.com','sy5259@163.com']

#emailRe= ["johnsonshi@dengtacj.com","xuebinliu@dengtacj.com","davidwei@dengtacj.com","steve@dengtacj.com","bgirlyang@dengtacj.com","waynettwan@dengtacj.com","alexzou@dengtacj.com","kevintian@dengtacj.com"]
#emailRe2= ['johnsonshi@dengtacj.com','sy5259@163.com','bgirlyang@dengtacj.com']

def getTime():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")

def sendEmail(zip,emailRe,log):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject']=log["title"]
    #    msgRoot['From'] = 'ota-build<'+emailSender+">"
    msgRoot['From'] = emailSender
    msgRoot['To'] = COMMASPACE.join(emailRe)
    strBody=log["result"]
    msgText = MIMEText(strBody,_subtype='html',_charset='utf-8')
    msgRoot.attach(msgText)
    
    part=MIMEBase('application','octet-stream')
    part.set_payload(open(zip,'rb').read())
    Encoders.encode_base64(part)
    filename=os.path.basename(zip)
    part.add_header('Content-Disposition', 'attachment; filename="'+filename+'"')
    msgRoot.attach(part)
    
	
    smtp = smtplib.SMTP()
    smtp.connect('smtp.mxhichina.com')
#    smtp.connect('smtp.163.com')
    smtp.login(emailSender,emailPassword)
    smtp.sendmail(emailSender, emailRe, msgRoot.as_string())
    smtp.quit()
    print('sendemail')

def analyseLog(logPath):
    if not os.path.exists(logPath+'/statistics.txt'):
        print(logPath+'/statistics.txt')
        print('statistics.txt file not exist')
        sys.exit(0)

    date = getTime()
    log={}
    f=open(logPath+'/statistics.txt',"r")
    logAll=f.readlines()
    f.close()
    title=""
    body=""
    for line in logAll:
        if "ANR" in line or "CRASH" in line or "tombstones" in line or "OOM" in line:
            tmp=line.replace("\n","").split("=")
            if tmp[1] !="0":
                title=title+tmp[0]+"次数:"+tmp[1]+"   "
        elif "build id" in line:
            body="执行设备:"+line.replace("\n","").split("=")[1]

    if title=="":
        title ='[Monkey Pass]'
    else:
        title = '[Monkey Error '+date+']'+title
    log["title"]=title
    print(title)

    f_comment=open(logPath+'/comments.csv',"r")
    logAllComment=f_comment.readlines()
    f_comment.close()

    ANRFlag=0
    tombstoneFlag=0
    OOMFlag=0
    CrashFlag=1

    LogResult=""
    Crash=""
    for line in logAllComment:
        if "Error:" in line:
            print(line)
            arrtmp=line.replace("\n","").split(",")
            #errorType=arrtmp[1].replace(";","").split(":")[1]
            ArrErrorType=arrtmp[1].split(":")[1].split(";")
            errorLog=logPath+"/log/"+arrtmp[2]
            ArrErrorType.remove("")
            for errorType in ArrErrorType:
                if errorType=="ANR" and ANRFlag==0:
                    ANRLog=getLog(errorType,errorLog)
                    ANRFlag=1
                    LogResult=LogResult+"<b>ANR log(更多见附件):</b><br>"+ANRLog+"<br><br><br>"
                elif errorType=="tombstones" and tombstoneFlag==0:
                    tombstoneLog=getLog(errorType,errorLog)
                    tombstoneFlag=1
                    LogResult=LogResult+"<b>tombstones log(更多见附件):</b><br>"+tombstoneLog+"<br><br><br>"
                elif errorType=="OOM" and OOMFlag==0:
                    OOMLog=getLog(errorType,errorLog)
                    OOMFlag=1
                    LogResult=LogResult+"<b>OOM log(更多见附件):</b><br>"+OOMLog+"<br><br><br>"
                elif errorType=="CRASH":
                    CrashLog=getLog(errorType,errorLog)
                    Crash=Crash+"Crash "+str(CrashFlag)+":<br>"+CrashLog+"<br><br>"
                    CrashFlag=CrashFlag+1

    if Crash!="":
        LogResult="<b>CRASH log:</b><br>"+Crash+LogResult

    if LogResult =="":
        LogResult="android monkey pass,更多见附件"
    log["result"]=LogResult
    print(log)
    return log

def getLog(type,logfile):
    if type=="CRASH":
        grepLog="System.err"
    elif type=="ANR":
        grepLog="E/ActivityManager"
    elif type=="tombstones":
        grepLog="I/DEBUG"
    elif type=="OOM":
        grepLog="System.err"

    (status, output) = commands.getstatusoutput('cat '+logfile+'|grep '+grepLog)
    print(status, output)
    return output.replace("\n","<br>")

if __name__ == "__main__":
    
    if sys.argv[2]=="one":
        emailRe=["275523330@qq.com","johnsonshi@dengtacj.com"]
    else:
        emailRe=["johnsonshi@dengtacj.com","bgirlyang@dengtacj.com","xuebinliu@dengtacj.com","davidwei@dengtacj.com","steve@dengtacj.com","kevintian@dengtacj.com"]
        #emailRe=["275523330@qq.com"]
    log=analyseLog(sys.argv[3])
    sendEmail(sys.argv[1],emailRe,log)

		
		
