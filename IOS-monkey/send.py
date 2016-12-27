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
import ConfigParser

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

def sendEmail(path,url,folder,emailRe):
    if path=="":
        strBody="IOS monkey 没有执行，请检查！"
    else:
        f=open(path+folder+"/index.html",'r')
        html_tmp=f.read()
        f.close()
    
        html_t=html_tmp.replace('href="','href="'+url+folder+'/')
        strBody="IOS monkey 执行结果，请点击查看\n <br><br><a href='"+url+folder+"/index.html'>"+url+folder+"/index.html"+"</a> <br><br>"+html_t
    
    date=getTime()
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = '[IOS Monkey Result]'+date
    #    msgRoot['From'] = 'ota-build<'+emailSender+">"
    msgRoot['From'] = emailSender
    msgRoot['To'] = COMMASPACE.join(emailRe)

    #strBody=html_t
    msgText = MIMEText(strBody,_subtype='html',_charset='utf-8')
    msgRoot.attach(msgText)
    
    #att = MIMEText(open(url+"/bootstrap.css", 'rb').read(), 'base64', 'cp936')
    #att["Content-Type"] = 'application/octet-stream'
    #att["Content-Disposition"] = ('attachment; filename=bootstrap.css')
    #msgRoot.attach(att)
    
    smtp = smtplib.SMTP()
    smtp.connect('smtp.mxhichina.com')
#    smtp.connect('smtp.163.com')
    smtp.login(emailSender,emailPassword)
    smtp.sendmail(emailSender, emailRe, msgRoot.as_string())
    smtp.quit()
    print 'sendemail'
	
if __name__ == "__main__":
    
    if sys.argv[4]=="one":
        emailRe=['johnsonshi@dengtacj.com',"275523330@qq.com","sy5259@163.com"]
    else:
        emailRe=["johnsonshi@dengtacj.com","bgirlyang@dengtacj.com","xuebinliu@dengtacj.com","alexzou@dengtacj.com","waynettwan@dengtacj.com","davidwei@dengtacj.com","steve@dengtacj.com","kevintian@dengtacj.com"]
        #emailRe=["275523330@qq.com","sy5259@163.com"]
    sendEmail(sys.argv[1],sys.argv[2],sys.argv[3],emailRe)

		
		
