#encoding:utf-8

import os
import sys
import datetime
from threading import Thread
import threading
import subprocess
import smtplib
from email.mime.image import MIMEImage
from email.MIMEText import MIMEText 
from email.MIMEMultipart import MIMEMultipart
import time
import config
import commands
import numpy as np
#import matplotlib.pyplot as pl
import pylab as pl
from pylab import *
import paramiko
from matplotlib.ticker import MultipleLocator
import types

global device


def getTime():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def run_cmd(cmd):
    process = subprocess.Popen(cmd , shell = True, stdout=subprocess.PIPE)
    return process.stdout.read().strip()

def timestamp_datetime(value):
    value = time.localtime(value)
    dt = time.strftime('%Y-%m-%d %H:%M:%S', value)
    return dt

#获取设备型号
def get_model():
    return run_cmd('adb -s '+device+' shell getprop ro.product.model')

#获取Android版本
def get_androidVersion():
    return run_cmd('adb -s '+device+' shell getprop ro.build.version.release')

#获取CPU型号
def get_cpuInfo():
    return run_cmd('adb -s '+device+' shell getprop ro.product.cpu.abi')

#获取系统编译版本增量
def get_buildVersionIncremental():
    return run_cmd('adb -s '+device+' shell getprop ro.build.version.incremental')

#获取系统编译时间
def get_buildDate():
    return run_cmd('adb -s '+device+' shell getprop ro.build.date.utc')

#获取apk版本
def get_APKVersion():
    return run_cmd("adb -s "+device+" shell dumpsys package com.dengtacj.stock |grep versionCode |awk -F ' ' '{print $1}'")

#同步获取cpu线程
#path:写cpu信息的文件路径
#count:获取次数
#updateTime:刷新次数
class CpuThread(threading.Thread):
    def __init__(self,path,count,updateTime):
        threading.Thread.__init__(self)
        self.thread_stop = False
        self.path = path
        self.count = count
        self.updateTime = int(updateTime)
    
    def run(self):
        if not self.thread_stop:
            time.sleep(30)
            log_output("Cpu thread is start")
            self.output = open(self.path, 'w+')
            for i in range(self.count):
                log_output("Cpu thread run count:" + str(i) + " "+time.strftime('%Y-%m-%d %X', time.localtime( time.time())))
                self.output.write(run_cmd("adb -s "+device+" shell top -n 1 ")  + "\n[recordTime:]" + time.strftime('%Y-%m-%d %X', time.localtime( time.time())) + "\n")
                time.sleep(self.updateTime)
            self.output.close()
            log_output("Cpu thread is stop")
    
    def stop(self):
        self.thread_stop = True

#同步获取mem线程
#path:写mem信息的文件路径
#count:获取次数
#updateTime:刷新次数
class MemThread(threading.Thread):
    def __init__(self,path,count,updateTime):
        threading.Thread.__init__(self)
        self.thread_stop = False
        self.path = path
        self.count = count
        self.updateTime = int(updateTime)
    
    def run(self):
        if not self.thread_stop:
            time.sleep(30)
            log_output("Mem thread is start")
            self.output = open(self.path, 'w+')
            for i in range(self.count):
                log_output("Mem thread run count:" + str(i) + " "+time.strftime('%Y-%m-%d %X', time.localtime( time.time())))
                self.output.write(run_cmd("adb -s "+device+" shell procrank") + "\n[recordTime:]" + time.strftime('%Y-%m-%d %X', time.localtime( time.time())) +"\n")
                time.sleep(self.updateTime)
            self.output.close()
            log_output("Mem thread is stop")
    
    def stop(self):
        self.thread_stop = True


#同步获取mem线程
#path:写mem信息的文件路径
#count:获取次数
#updateTime:刷新次数
class MonkeyThread(threading.Thread):
    def __init__(self,cmd):
        threading.Thread.__init__(self)
        self.thread_stop = False
        self.cmd = cmd
    
    def run(self):
        if not self.thread_stop:
            log_output("start monkey")
            run_cmd(self.cmd)
            log_output("monkey stop")
    
    def stop(self):
        self.thread_stop = True

def log_output(log):
    #可以优化，不用一一直打开关闭
    print "[LOG]:"+log
    f=open('log.txt','a')
    f.write('['+config.getTime(1)+']: '+log +'\n')
    f.close()
'''
def get_configValue(type,key):
    sep = os.path.sep   #获取系统分隔符
    path = sys.path[0]  #获取脚本路径
    
    conf_path = path + sep + "systemMonitor.conf"   #监控配置文件
    
    #读取配置文件
    cf = ConfigParser.ConfigParser()
    cf.read(conf_path)
    return cf.get(type,key)
'''

def env_prepare():

    #准备日志
    if os.path.exists(config.logpath):
        os.remove(config.logpath)

    #检查输出目录是否存在
    if not os.path.exists(config.outpath):
        os.mkdir(config.outpath)

    #检查历史记录目录是否存在
    if not os.path.exists(config.historypath):
        os.mkdir(config.historypath)

    #检查apk目录是否存在
    if not os.path.exists(config.apkpath):
        os.mkdir(config.apkpath)

    out_path = config.outpath + config.sep + config.now_time
    os.mkdir(out_path)

    #检查环境配置
    if config.runTime == "" or config.runTime == 0:
        log_output("runTime is null")
        sys.exit()
    if config.updateTime == "" or config.updateTime == 0:
        log_output("updateTime is null")
        sys.exit()
    if config.packageNameList == "":
        log_output("packageNameList is null")
        sys.exit()


#分析CPU
def analysisCPU(filePath):
    if not os.path.exists(filePath):
        log_output("Path is not exist:"+filePath)
        sys.exit()

    path = os.path.dirname(filePath)
    dict_cpu={}
    cpu_user_list = []
    cpu_system_list = []
	#分析系统cpu
    os.system("cat "+filePath+"|grep , >"+path+ config.sep +"system_cpu.txt")
    log_output("system cpu file:"+path+ config.sep +"system_cpu.txt")

    fp = open(path + config.sep +"system_cpu.txt")
    try:
        lines = fp.readlines()
    finally:
        fp.close()
	for line in lines:
            line_split = line.strip().rstrip('\r').lstrip().split(' ')
            cpu_user_list.append(int(line_split[1].replace('%,','')))
            cpu_system_list.append(int(line_split[3].replace('%,','')))

	dict_cpu["user"]=cpu_user_list
	dict_cpu["system"]=cpu_system_list

    #分析app cpu

    for packageName in config.packageNameList:
        cpu_list = []
        os.system('cat '+filePath+'|grep "'+packageName+'\r" >'+path+ config.sep + packageName+'_cpu.txt')
        log_output("["+packageName+"] cpu file:"+path+ config.sep +packageName+"_cpu.txt")
        fp = open(path + config.sep +packageName+"_cpu.txt")
        try:
			lines = fp.readlines()
        finally:
            fp.close()
        for line in lines:
            line_split = line.strip().rstrip('\r').lstrip().split(' ')
            for j in line_split:
                if "%" in j:
                    cpu_list.append(int(j.replace('%','')))
		dict_cpu[packageName+"_cpu"]=cpu_list
	
	#记录时间

    time_list=[]
    os.system("cat "+filePath+"|grep recordTime >"+path+ config.sep +"time_cpu.txt")
    log_output("record cpu time file:"+path+ config.sep +"time_cpu.txt")

    fp = open(path + config.sep +"time_cpu.txt")
    try:
        lines = fp.readlines()
    finally:
        fp.close()
	for line in lines:
		line_split = line.strip().rstrip('\r').lstrip().split(' ')
		time_list.append(line_split[1])
	dict_cpu["time_cpu"]=time_list
    dict_result={}
    tmp=0
    for k in dict_cpu:
        if tmp==0:
            tmp=len(dict_cpu[k])
        elif len(dict_cpu[k])<tmp:
            tmp=len(dict_cpu[k])

    for k in dict_cpu:
        dict_result[k]=dict_cpu[k][0:tmp]

    return dict_result


#分析MEM信息
def analysisMEM(filePath):
    if not os.path.exists(filePath):
        log_output("Path is not exist:"+filePath)
        sys.exit()
    
    path = os.path.dirname(filePath)
    dict_mem={}
	#分析系统内存
    os.system("cat "+filePath+"|grep total >"+path+ config.sep +"system_mem.txt")
    mem_system_list = []
    log_output("system mem file:"+path+ config.sep +"system_mem.txt")

    fp = open(path + config.sep +"system_mem.txt")
    try:
        lines = fp.readlines()
    finally:
        fp.close()
	for line in lines:
		line_split = line.strip().rstrip('\r').lstrip().split(' ')
		system_mem = int(line_split[1].replace('K','')) - int(line_split[3].replace('K',''))
		mem_system_list.append(round(system_mem/float(1024),2))
	dict_mem["system"]=mem_system_list

    #分析app内存

    for packageName in config.packageNameList:
        pss_list = []
        uss_list = []
        os.system('cat '+filePath+'|grep "'+packageName+'\r" >'+path+ config.sep + packageName+'_mem.txt')
        log_output("["+packageName+"] mem file:"+path+ config.sep +packageName+"_mem.txt")
        fp = open(path + config.sep +packageName+"_mem.txt")
        try:
            lines = fp.readlines()
        finally:
            fp.close()
        for line in lines:
                line_split = line.strip().rstrip('\r').lstrip().split('K')
                pss_list.append(round(int(line_split[2].strip())/float(1024),2))

            #uss_list.append(line_split[4].split(' ')[0].replace('K',''))
        dict_mem[packageName+"_mem"]=pss_list
            #dict_mem[packageName+"uss"]=uss_list
			
	
	#记录时间

    time_list=[]
    os.system("cat "+filePath+"|grep recordTime >"+path+ config.sep +"time_mem.txt")
    log_output("record mem time file:"+path+ config.sep +"time_mem.txt")
    fp = open(path + config.sep +"time_mem.txt")
    try:
        lines = fp.readlines()
    finally:
        fp.close()
	for line in lines:
		line_split = line.strip().rstrip('\r').lstrip().split(' ')
		time_list.append(line_split[1])
	dict_mem["time_mem"]=time_list
    dict_result={}
    tmp=0
    for k in dict_mem:
        if tmp==0:
            tmp=len(dict_mem[k])
        elif len(dict_mem[k])<tmp:
            tmp=len(dict_mem[k])

    for k in dict_mem:
        dict_result[k]=dict_mem[k][0:tmp]
    return dict_result


def run_record():

    (status,output)=commands.getstatusoutput("adb devices")
    if status != 0 or len(output)== 26:
        print output
        log_output("请检查连接的手机")
        sys.exit()
    
    run_cmd("adb -s "+device+" wait-for-devices root")
    run_cmd("adb -s "+device+" wait-for-devices remount")

    run_times=config.runTime*800

    package=""
    for packageName in config.packageNameList:
        run_cmd("adb -s "+device+" shell am force-stop "+packageName)
        package = package + " -p "+packageName

    monkey_command="monkey --throttle 500 "+package+" --ignore-crashes --monitor-native-crashes --ignore-timeouts --ignore-native-crashes --pct-touch 25 --pct-motion 20 --pct-trackball 25 --pct-nav 5 --pct-majornav 5 --pct-syskeys 0 --pct-appswitch 20 --pct-flip 0 --pct-anyevent 0 -v -v -v "+str(run_times)

    log_output(monkey_command)
    #计算top命令-n参数的值,即刷新多少次
    getCount = config.runTime * 60/config.updateTime
    
    log_output("[runTime]:" + str(config.runTime))
    log_output("[updateTime]:" + str(config.updateTime))
    log_output("[count]:" + str(getCount))

    log_output("start run monkey and record mem & cpu")

    unlockDevice()
    threads = []
    
    #开始执行获取cpu线程
    t1 = CpuThread(config.cpu_log_path,getCount,config.updateTime)
    
    #开始执行获取mem线程
    t2 = MemThread(config.mem_log_path,getCount,config.updateTime)

    #开始执行monkey
    t3 = MonkeyThread("adb -s "+device+" shell "+monkey_command)

    threads.append(t3)
    threads.append(t2)
    threads.append(t1)
    
    #开始执行所有线程
    for t in threads:
        t.start()
    
    #等待所有线程结束
    for t in threads:
        t.join()

    log_output("finish run monkey and record mem & cpu")

def record_history(mem_dict,cpu_dict):
    #user_cpu=str(np.mean(cpu_dict["user"],dtype=int32))
    dengta_cpu=str(np.mean(cpu_dict["com.dengtacj.stock_cpu"],dtype=int32))
    dengta_mem=str(np.mean(mem_dict["com.dengtacj.stock_mem"],dtype=int32))
    
    now_time=getTime().split(" ")[0]
    f=open(config.historyfile,"a")
    f.write(now_time+" "+dengta_cpu+" "+dengta_mem+"\n")
    f.close()
    log_output("record history file:["+now_time+" "+dengta_cpu+" "+dengta_mem +"]")
    


def analyse_log():
    #tmp_path = config.outpath + config.sep + config.now_time + config.sep +"tmp"
    #if not os.path.exists(tmp_path):
    #    os.mkdir(tmp_path)

    mem_dict=analysisMEM(config.mem_log_path)
    cpu_dict=analysisCPU(config.cpu_log_path)

    record_history(mem_dict,cpu_dict)
    #画mem
    draw(u"内存检测",mem_dict,u"时间轴",u"消耗内存(M)",config.mem_png_path)
    #画cpu
    draw(u"CPU检测",cpu_dict,u"时间轴",u"所占cpu(%)",config.cpu_png_path)
    #画历史mem趋势
    #画历史cpu趋势
    draw_trend()

def draw(title,data,x_title,y_title,png_path):
    
    fig = pl.figure(figsize=(10,6))

    all=[]
    
    
    if "CPU" in title:
        tmp="%"
        n="_cpu"
        num=10
        x=np.arange(0,len(data["time"+n]),1)
        log_output("draw user cpu line")
        pl.plot(x,data["user"],label=u"User平均值: "+str(np.mean(data["user"],dtype=int32))+tmp,color='green')
        color_list = ['blue','black','cyan','magenta','yellow']
        all.append(data["user"])
    else:
        tmp="M"
        n="_mem"
        num=200
        x=np.arange(0,len(data["time"+n]),1)
        color_list = ['green','blue','black','cyan','magenta','yellow']
    log_output("draw system "+n+" line")
    pl.plot(x,data["system"],label=u"System平均值: "+str(np.mean(data["system"],dtype=int32))+tmp,color='red')
    all.append(data["system"])

    x_time=[]
    for i in range(0,len(data["time"+n])):
        if i % 9 ==0:
            x_time.append(data["time"+n][i])
    #color_list=['r','g','b']
    #color_list = ['red','green','yellow','blue','black','cyan','magenta']

		
    i=0
    for package in config.packageNameList:
        log_output("draw "+package+" "+n+" line")
        pl.plot(x,data[package+n],label="["+config.packageNameDict[package]+u"]平均值: "+str(np.mean(data[package+n],dtype=int32))+tmp,color=color_list[i])
        i=i+1
        all.append(data[package+n])
	
	
    ax =pl.gca()

    pl.ylim(0,np.max(all)*1.3)
    pl.xlim(1,np.max(x))
    
    #设置图的底边距
    pl.subplots_adjust(bottom=0.15)
    
    #开启网格
    pl.grid()
    
    #主刻度
    ax.xaxis.set_major_locator(MultipleLocator(9))
    ax.yaxis.set_major_locator(MultipleLocator(num))
    
    #获取当前x轴的label
    locs,labels = pl.xticks()
    
    #重新设置新的label,用时间设置
    pl.xticks(locs,x_time)
    
    pl.xlabel(x_title)
    pl.ylabel(y_title)
    pl.title(title)
    
    pl.legend()
    fig.autofmt_xdate()
    pl.savefig(png_path)
    log_output("save png file: "+png_path)
#pl.show()

def draw_trend():
    pl.clf()
    fig = pl.figure()
    tmp = np.loadtxt(config.historyfile,dtype=str)
    tmp1=[]
    #time = np.genfromtxt(config.historyfile,usecols=(1),delimiter=',',dtype=None)
    
    if  type(tmp[0]) == np.string_:
        tmp1.append(tmp)
        data=np.array(tmp1)
    else:
        data=tmp
    x=np.arange(0,len(data[:,0]),1)
    #mem
    pl.plot(x, data[:,2],label=u"灯塔MEM平均值曲线",color='r')
    ax =pl.gca()
    pl.xlabel(u"日期")
    pl.ylabel(u"内存(M)")
    pl.ylim(0,np.max(map(eval,data[:,2]))*1.3)
    pl.xlim(1,np.max(x))
    
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(20))
    #获取当前x轴的label
    locs,labels = pl.xticks()
    
    #重新设置新的label,用时间设置
    pl.xticks(locs,data[:,0])
    pl.title(u"内存趋势")
    
    pl.legend()
    fig.autofmt_xdate()
    pl.savefig(config.mem_trend_path)
    log_output("save mem trend png file: "+config.mem_trend_path)
    
    pl.clf()
#pl.show()
    #cpu
    pl.plot(x, data[:,1],label=u"灯塔CPU平均值曲线",color='r')
#pl.plot(x, data[:,2],label=u"System CPU平均值曲线",color='b')
    ax =pl.gca()
    pl.xlabel(u"日期")
    pl.ylabel(u"CPU(%)")
    pl.ylim(0,np.max(map(eval,data[:,1]))*1.3)
    pl.xlim(1,np.max(x))
    
    #获取当前x轴的label
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    locs,labels = pl.xticks()
    
    #重新设置新的label,用时间设置
    pl.xticks(locs,data[:,0])
    pl.title(u"CPU趋势")
    
    pl.legend()
    fig.autofmt_xdate()
    pl.savefig(config.cpu_trend_path)
    log_output("save cpu trend png file: "+config.cpu_trend_path)


def send_email(startTime,stopTime):
    print "start send email"
	#获取设备信息
    model = get_model()
    androidVersion = get_androidVersion()
    cpuInfo = get_cpuInfo()
    buildVersionIncremental = get_buildVersionIncremental()
    buildDate = timestamp_datetime(float(get_buildDate()))
    apkVersion=get_APKVersion()
    msg = MIMEMultipart('related')
    msg['Subject']=u"Dengta("+apkVersion+")--Android性能测试报告--测试设备:("+model+")"
    msg['From']=config.me
    msg['To']=';'.join(config.mailto_list)
    
    content = ""
    content+="<html>"
    content+="<head>"
    content+="<meta http-equiv=Content-Type content=\"text/html;charset=gb2312\">"
    content+="<style type=\"text/css\">"
    content+="body {font-family:\"" + "微软雅黑".decode('UTF-8').encode('GBK') + "\",\"宋体\",\"黑体\",Arial,Tahoma,Geneva,sans-serif;}"
    content+="table {width:90%;border:2px solid;border-collapse:collapse;}"
    content+="th {border-width:2px;border-style:solid;border-color:black;text-align:center;width:150px;background-color:#AEEEEE;color:red;}"
    content+="td {border-width:2px;border-style:solid;}"
    content+="</style>"
    content+="</head>"
    content+="<body>"
    content+="<span><b>Dengta版本:".decode('UTF-8').encode('GBK') + str(apkVersion) + "</b><span>"
    #content+="<body><table border='1'>"
    #content+="<tr><td>Dengta版本</td><td>".decode('UTF-8').encode('GBK') + str(apkVersion) + "</td></tr></table>"
    content += "<br/>"
    content+="<span><b>运行时长(分):".decode('UTF-8').encode('GBK') + str(config.runTime) + "</b><span>"
    content += "<br/>"
    content+="<span><b>开始时间:".decode('UTF-8').encode('GBK') + startTime + "</b><span>"
    content += "<br/>"
    content+="<span><b>结束时间:".decode('UTF-8').encode('GBK') + stopTime + "</b><span>"
    content += "<br/><br/>"
    content+="<span><b>刷新次数:".decode('UTF-8').encode('GBK') + str(config.runTime * 60/config.updateTime) + "</b><span>"
    content += "<br/>"
    content+="<span><b>刷新频率(秒):".decode('UTF-8').encode('GBK') + str(config.updateTime) + "</b><span>"
    content += "<br/>"
    content+="<span><b>设备名称:".decode('UTF-8').encode('GBK') + str(model) + "</b><span>"
    content += "<br/>"
    content+="<span><b>系统版本:".decode('UTF-8').encode('GBK') + str(androidVersion) + "</b><span>"
    #开始执行monke
    content += "<br/>"
    content+="<span><b>CPU信息:".decode('UTF-8').encode('GBK') + str(cpuInfo) + "</b><span>"
    content += "<br/>"
    content+="<span><b>系统编译增量:".decode('UTF-8').encode('GBK') + str(buildVersionIncremental) + "</b><span>"
    content += "<br/>"
    content+="<span><b>系统编译日期:".decode('UTF-8').encode('GBK') + str(buildDate) + "</b><span>"
    content += "<br/>"
    
    content += "<br/>"
    content+="<span><b>名词解释:</b><span>".decode('UTF-8').encode('GBK')
    content += "<br/>"
    content+="<span><b>PSS:实际使用的物理内存</b><span>".decode('UTF-8').encode('GBK')
    content += "<br/>"
    content+="<span><b>USS:进程独自占用的物理内存</b><span>".decode('UTF-8').encode('GBK')
    content += "<br/>"
    
    content += "<br/>"
    content+="<span><b>System性能趋势:</b><span>".decode('UTF-8').encode('GBK')
    #content+="<span><b>" + system_maxminavg.decode('UTF-8').encode('GBK') + "</b><span>"
    content += "<br/>" 
    content += "<img src=\"cid:cpu.png\" alt=\"cpu.png\">"
    content += "<br/>"
    content += "<br/>"
 
    content += "<img src=\"cid:mem.png\" alt=\"mem.png\">"
    content += "<br/>"
    content += "<br/>"
    
    content+="<span><b>灯塔趋势:</b><span>".decode('UTF-8').encode('GBK')
    #content+="<span><b>" + system_maxminavg.decode('UTF-8').encode('GBK') + "</b><span>"
    content += "<br/>" 
    content += "<img src=\"cid:cpu_trend.png\" alt=\"cpu_trend.png\">"
    content += "<br/>"
    content += "<br/>"
 
    content += "<img src=\"cid:mem_trend.png\" alt=\"mem_trend.png\">"
    content += "<br/>"
    content += "<br/>"
    content+="</body>"
    content+="</html>"
    
    msg.attach(MIMEText(content,_subtype='html',_charset='gb2312'))

    fp = open(config.cpu_png_path,'rb')
    img = MIMEImage(fp.read())
    img.add_header('Content-ID',"cpu.png")
    msg.attach(img)
        
    fp = open(config.mem_png_path,'rb')
    img = MIMEImage(fp.read())
    img.add_header('Content-ID',"mem.png")
    msg.attach(img)
   
    fp = open(config.cpu_trend_path,'rb')
    img = MIMEImage(fp.read())
    img.add_header('Content-ID',"cpu_trend.png")
    msg.attach(img)
        
    fp = open(config.mem_trend_path,'rb')
    img = MIMEImage(fp.read())
    img.add_header('Content-ID',"mem_trend.png")
    msg.attach(img)
 
    try:
        ott_mail=smtplib.SMTP()
        ott_mail.connect(config.mailserver)
        ott_mail.login(config.user, config.password)
        ott_mail.sendmail(config.me,config.mailto_list,msg.as_string())
        ott_mail.close()
        print "sendEmail OK"
        log_output("send Email ok")
        return True
    except Exception,e:
        print e
        print "sendEmail fail"
        #log_output("send Email fail:"+e)
        return False




def ssh2(ip,port,username,passwd,cmd):
    try:
        #paramiko.util.log_to_file("a.log")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,port,username,passwd)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result=stdout.read()
        #           stdin.write("Y")   #简单交互，输入 ‘Y’
        #out = stdout.readlines()
        #屏幕输出
        #for o in out:
        #    print o,
        #print '%s\tOK\n'%(ip)
        ssh.close()
        print result
        return result
    except :
        print '%s\tError\n'%(ip)


def remote_scp(host_ip,port,username,password,remote_path,local_path):
    
    t = paramiko.Transport((host_ip,port))
    
    t.connect(username=username, password=password)  # 登录远程服务器
    
    sftp = paramiko.SFTPClient.from_transport(t)   # sftp传输协议
    
    src = remote_path
    
    des = local_path
    
    sftp.get(src,des)
    
    t.close()

def donwloadNewPackage():
    out=ssh2(config.ip,config.port,config.username,config.psw,"ls -t /data/android/history |grep -v dtv|head -1")
    apkfile=ssh2(config.ip,config.port,config.username,config.psw,"ls  -rt /data/android/history/"+out.strip().rstrip('\r')+" |head -1")
    log_output("download apk file:"+config.apkpath+apkfile)
    print "/data/android/history/"+out.strip().rstrip('\r')+"/"+apkfile
    remote_scp(config.ip,config.port,config.username,config.psw,"/data/android/history/"+out.strip().rstrip('\r')+"/"+apkfile.strip().rstrip('\r'),config.apkpath+apkfile.strip().rstrip('\r'))
    run_cmd("adb -s "+device+" install -r "+config.apkpath+apkfile.strip().rstrip('\r'))
    time.sleep(5)
    run_cmd("adb -s "+device+" shell am start -W com.dengtacj.stock/.main.MainActivity")
    time.sleep(1)
    run_cmd("adb -s "+device+" shell am force-stop com.dengtacj.stock")
    time.sleep(1)
    run_cmd("adb -s "+device+" shell am start -W com.dengtacj.stock/.main.MainActivity")


def unlockDevice():
    size = commands.getstatusoutput("adb shell wm size|awk '{print $NF}'")
    x=int(size[1].split("x")[0])
    y=int(size[1].split("x")[1])
    command = 'adb shell dumpsys SurfaceFlinger|grep "|....|"|awk \'BEGIN{r="o"}{if($NF=="com.android.systemui.ImageWallpaper"||$NF=="com.android.systemui.keyguard.leui.KeyguardImageWallpaper")r="l"}END{print NR-1 r}\''
    while True:
        stat=commands.getstatusoutput(command)
        if stat[1]=="1o":
            status=0
        elif stat[1]=="4o":
            status =1
        else:
            status=2

        if status==0:
            os.system("adb shell input keyevent 26&&sleep 1&&adb shell input swipe "+ str(x/2)+" "+str(4*y/5)+" "+str(x/2)+ " "+str(y/5))
        elif status==1:
            os.system("adb shell input swipe " + str(x / 2) + " " + str(4 * y / 5) + " " + str(x / 2) + " " + str(y / 5))
        else:
            break



if __name__=='__main__':

    if len(sys.argv)!=2:
        print "please give right arg:device"
        sys.exit(0)
    else:
        device=sys.argv[1]


    #环境准备
    env_prepare()

    #获取最新的apk
    donwloadNewPackage()

    #记录cpu，mem
    startTime=getTime()
    run_record()
    stopTime=getTime()

    #分析日志
    analyse_log()

    # startTime="2016-04-13 10:59:51"
    # stopTime="2016-04-13 12:31:44"

    #发送邮件
    send_email(startTime,stopTime)

