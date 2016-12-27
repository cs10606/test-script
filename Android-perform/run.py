#encoding:utf-8

import os
import sys
import datetime
from threading import Thread
import threading
import subprocess
import smtplib
from email.mime.image import MIMEImage
# from email.MIMEText import MIMEText
# from email.MIMEMultipart import MIMEMultipart
import time
import commands
import numpy as np
#import matplotlib.pyplot as pl
import pylab as pl
from pylab import *
import paramiko
from matplotlib.ticker import MultipleLocator
import types
import string
import calendar


global device

def getTime(type):
    now = datetime.datetime.now()
    if type ==1:
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif type ==0:
        return now.strftime("%Y%m%d_%H%M%S")




#运行时长,以秒为单位
runTime=600

#是否跑monkey
# MonkeyRun = True
MonkeyRun = False
#收件人,以逗号分隔
mailto_list=["johnsonshi@dengtacj.com"]
#mailto_list=["johnsonshi@dengtacj.com","xuebinliu@dengtacj.com","davidwei@dengtacj.com","steve@dengtacj.com","bgirlyang@dengtacj.com","kevintian@dengtacj.com","waynettwan@dengtacj.com","alexzou@dengtacj.com","kevintian@dengtacj.com"]

#邮件服务器参数
mailserver="smtp.mxhichina.com"
user="johnsonshi@dengtacj.com"
password="dengtacj@20151"
me="johnsonshi@dengtacj.com"

#获取当前执行时间戳
now_time = getTime(0)
#now_time="20160701_063211"
print now_time
sep = os.path.sep   #获取系统分隔符
path = sys.path[0]  #获取脚本路径
# workdir=path
#日志路径
#日志路径
#日志路径
logpath = path + sep + "log.txt"

#输出目录
outpath = path + sep + "out"


#apk目录
apkpath = path + sep + "apk" +sep

#远程登录信息
ip="192.168.9.26"
port=36000
username="devbase"
psw="devbase"

cpu_log_path = outpath + sep + now_time + sep + "monitor_cpu.txt"     #cpu日志文件
mem_log_path = outpath + sep + now_time + sep + "monitor_mem.txt"     #mem日志文件
fps_log_path = outpath + sep + now_time + sep + "monitor_fps.txt"     #fps日志文件


class ReportTemplate(string.Template):
    delimiter = '@'
    idpattern = r'[a-z][_a-z0-9]*'

def generateHtml(cpu_data,mem_data,fps_data):
    # read template
    filename = os.path.join(path + sep, 'template.html')

    html = None
    with open(filename, 'r') as f:
        html = f.read()
        f.close()
    if html is None:
        print 'read html template fail'
        return False
    template = ReportTemplate(html)
    render_data = {}

    render_data['cpudata'] = ','.join(cpu_data['cpu'])
    render_data['memdata'] = ','.join(mem_data['mem'])
    render_data['fpsdata'] = ','.join(fps_data['fps'])
    render_data['avg_cpu'] = cpu_data['avg_cpu']
    render_data['avg_mem'] = mem_data['avg_mem']
    render_data['avg_fps'] = fps_data['avg_fps']
    # render_data['workdir']=workdir


    out_data = template.substitute(render_data)
    # save
    outfile = os.path.join(outpath + sep + now_time + sep , 'report.html')
    with open(outfile, 'w') as f:
        f.write(out_data)
        f.close()
    return True


def run_cmd(cmd):
    process = subprocess.Popen(cmd , shell = True, stdout=subprocess.PIPE)
    return process.stdout.read().strip()

def timestamp_datetime(value):
    value = time.localtime(value)
    dt = time.strftime('%Y-%m-%d %H:%M:%S', value)
    return dt
#
# #获取设备型号
# def get_model():
#     return run_cmd('adb -s 5655d3d5 shell getprop ro.product.model')
#
# #获取Android版本
# def get_androidVersion():
#     return run_cmd('adb -s 5655d3d5 shell getprop ro.build.version.release')
#
# #获取CPU型号
# def get_cpuInfo():
#     return run_cmd('adb -s 5655d3d5 shell getprop ro.product.cpu.abi')
#
# #获取系统编译版本增量
# def get_buildVersionIncremental():
#     return run_cmd('adb -s 5655d3d5 shell getprop ro.build.version.incremental')
#
# #获取系统编译时间
# def get_buildDate():
#     return run_cmd('adb -s 5655d3d5 shell getprop ro.build.date.utc')
#
# #获取apk版本
# def get_APKVersion():
#     return run_cmd("adb -s 5655d3d5 shell dumpsys package com.dengtacj.stock |grep versionCode |awk -F ' ' '{print $1}'")

#同步获取cpu线程
#path:写cpu信息的文件路径
#count:获取次数
#updateTime:刷新次数
class RecordThread(threading.Thread):
    def __init__(self,type,path,cmd):
        threading.Thread.__init__(self)
        self.thread_stop = False
        self.path = path
        self.type = type
        self.cmd = cmd


    def run(self):
        i=0
        if self.type =="FPS":
            self.waitTime=3
        else:
            self.waitTime=0
        self.output = open(self.path, 'w+')
        print self.path

        log_output(self.type + " thread is start")
        while True:
            i+=1
            log_output(self.type+" thread run count:" + str(i) + " "+time.strftime('%Y-%m-%d %X', time.localtime( time.time())))
            self.output.write(str(int(time.time()))+" " +run_cmd(self.cmd)+" "+ time.strftime('%Y-%m-%d %X', time.localtime( time.time())) + '\n')
            time.sleep(self.waitTime)

    def stop(self):
        self.output.close()
        log_output(self.type+" thread is stop")
        self.thread_stop = True

#
# #同步获取mem线程
# #path:写mem信息的文件路径
# #count:获取次数
# #updateTime:刷新次数
# class MemThread(threading.Thread):
#     def __init__(self,path,count):
#         threading.Thread.__init__(self)
#         self.thread_stop = False
#         self.path = path
#         self.count = count
#
#     def run(self):
#         if not self.thread_stop:
#             log_output("Mem thread is start")
#             self.output = open(self.path, 'w+')
#             for i in range(self.count):
#                 log_output("Mem thread run count:" + str(i) + " "+time.strftime('%Y-%m-%d %X', time.localtime( time.time())))
#                 self.output.write(str(time.time())+" " +run_cmd("adb -s 5655d3d5 shell procrank |grep 'com.dengtacj.stock\r' ")+" "+ time.strftime('%Y-%m-%d %X', time.localtime( time.time())) +"\n")
#             self.output.close()
#             log_output("Mem thread is stop")
#
#     def stop(self):
#         self.thread_stop = True

# # 同步获取mem线程
# # path:写mem信息的文件路径
# # count:获取次数
# # updateTime:刷新次数
# class FPSThread(threading.Thread):
#     def __init__(self, path, count):
#         threading.Thread.__init__(self)
#         self.thread_stop = False
#         self.path = path
#         self.count = count
#
#     def run(self):
#         if not self.thread_stop:
#             log_output("FPS thread is start")
#             self.output = open(self.path, 'w+')
#             for i in range(self.count):
#                 log_output("FPS thread run count:" + str(i) + " "+time.strftime('%Y-%m-%d %X', time.localtime( time.time())))
#                 self.output.write(str(time.time()) + " " + run_cmd('adb shell dumpsys gfxinfo com.dengtacj.stock |sed -n -e "/Profile/,/hierarchy/p"') + " " + time.strftime(
#                     '%Y-%m-%d %X', time.localtime(time.time())) + "\n")
#                 time.sleep(1)
#             self.output.close()
#             log_output("FPS thread is stop")
#
#     def stop(self):
#         self.thread_stop = True


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
        proc=run_cmd("adb shell ps |grep monkey | awk '{print $2}'")
        run_cmd("adb -s "+device+" shell kill "+str(proc))

        self.thread_stop = True

def log_output(log):
    #可以优化，不用一一直打开关闭
    print "[LOG]:"+log
    f=open('log.txt','a')
    f.write('['+getTime(1)+']: '+log +'\n')
    f.close()


def env_prepare():

    #准备日志
    if os.path.exists(logpath):
        os.remove(logpath)

    #检查输出目录是否存在
    if not os.path.exists(outpath):
        os.mkdir(outpath)

    # #检查历史记录目录是否存在
    # if not os.path.exists(config.historypath):
    #     os.mkdir(config.historypath)

    #检查apk目录是否存在
    if not os.path.exists(apkpath):
        os.mkdir(apkpath)

    out_path = outpath + sep + now_time
    os.mkdir(out_path)

    #检查环境配置
    if runTime == "" or runTime == 0:
        log_output("runTime is null")
        sys.exit()

    #打开gpu记录到gfxinfo中
    run_cmd('adb shell setprop debug.hwui.profile true')

    #重启app来生效
    run_cmd('adb shell am force-stop com.dengtacj.stock')
    run_cmd('adb shell am start -W com.dengtacj.stock/.main.MainActivity')




#分析CPU
def analysisCPU(filePath):
    if not os.path.exists(filePath):
        log_output("Path is not exist:"+filePath)
        sys.exit()

    data = {}
    cpudata=[]
    count = 0
    size = 0

    #分析app cpu
    fp = open(filePath)
    try:
        lines = fp.readlines()
    finally:
        fp.close()
    for line in lines:
        line_split = line.strip().rstrip('\r').lstrip().split(' ')
        for j in line_split:
            if "%" in j:
                # ts = int(calendar.timegm(int(line_split[0]).timetuple()) * 1000)
                # ts= "%.0lf" % float(line_split[0])
                # ts= float(line_split[0])*1000
                ts = (int(line_split[0]) + 8 * 60 * 60) * 1000
                cpudata.append('[%.0u, %.2f]' % (ts, float(j.replace('%',''))))
                count+=int(j.replace('%',''))
                size += 1

    if size != 0:
        avg = count / size

    data["avg_cpu"]=avg
    data["cpu"]=cpudata
    print data
    return data


#分析MEM信息
def analysisMEM(filePath):
    if not os.path.exists(filePath):
        log_output("Path is not exist:"+filePath)
        sys.exit()

    memdata = []
    data = {}
    count = 0
    size = 0

    fp = open(filePath)
    try:
        lines = fp.readlines()
    finally:
        fp.close()
    for line in lines:
        line_split = line.strip().rstrip('\n').lstrip().split('K')
        # ts = int(calendar.timegm(int(line_split[0].split(" ")[0]).timetuple()) * 1000)
        # ts = "%.0lf" % float(line_split[0].split(" ")[0])
        # ts = float(line_split[0].split(" ")[0])*1000
        ts = (int(line_split[0].split(" ")[0]) + 8 * 60 * 60) * 1000
        memdata.append('[%.0u, %.2f]' % (ts, float(line_split[2].strip())/float(1024)))
        count+=float(line_split[2].strip())/float(1024)
        size += 1

    if size != 0:
        avg = int(count / size)
    data["avg_mem"]=avg
    data["mem"]=memdata
    print data
    return data


def analysisFPS(filepath):
    if not os.path.exists(filepath):
        log_output("gfxinfo文件不存在")
        sys.exit(0)

    # activity_list = []
    # frame_list = []
    # jank_list = []
    fps_list = []
    fps_data={}


    recordFlag = False
    # activity = ""
    frame_count = 0
    jank_count = 0
    vsync_overtime = 0

    count=0
    size=0


    f = open(filepath, 'r')
    lines = f.readlines()
    for line in lines:
        if "Profile" in line:
            r_time=  line.strip().split(" ")[0]
        elif "com.dengtacj.stock" in line:
            recordFlag = True
            activity = line.split("/")[1]
        elif line.strip() == "" and recordFlag:
            if frame_count <> 0:
                fps = int(frame_count * 60 / (frame_count + vsync_overtime))
                count += fps
                size += 1
                # ts = int(calendar.timegm(int(r_time).timetuple()) * 1000)
                # ts = "%.0lf" % float(r_time)
                # ts = float(r_time)*1000
                ts = (int(r_time) + 8 * 60 * 60) * 1000
                fps_list.append('[%.0u, %d]' % (ts, fps))
                # activity_list.append(activity)
                # frame_list.append(frame_count)
                # jank_list.append(jank_count)
                # fps_list.append(fps)
                # print activity + ":frame_count=" + str(frame_count) + ";jank_count=" + str(jank_count) + ";fps=" + str(
                #     fps)
                # frame_count = 0
                # jank_count = 0
                # vsync_overtime = 0
                # recordFlag = False
                # activity = ""
        elif recordFlag:
            if not "Draw" in line:
                frame_count = frame_count + 1
                time_block = line.strip().split("\t")
                try:
                    render_time = float(time_block[0]) + float(time_block[1]) + float(time_block[2])
                except Exception, e:
                    render_time = 0

                if render_time > 16.67:
                    jank_count += 1
                    if render_time % 16.67 == 0:
                        vsync_overtime += int(render_time / 16.67) - 1
                    else:
                        vsync_overtime += int(render_time / 16.67)

    if size != 0:
        avg = count / size
    fps_data["avg_fps"]=avg
    fps_data["fps"]=fps_list
    print fps_data
    return fps_data

def run_record():

    (status,output)=commands.getstatusoutput("adb devices")
    if status != 0 or len(output)== 26:
        print output
        log_output("请检查连接的手机")
        sys.exit()
    
    run_cmd("adb -s "+device+" wait-for-devices root")
    run_cmd("adb -s "+device+" wait-for-devices remount")

    runTimes=runTime*11
    # monkey_command="monkey --throttle 500 "+package+" --ignore-crashes --monitor-native-crashes --ignore-timeouts --ignore-native-crashes --pct-touch 25 --pct-motion 20 --pct-trackball 25 --pct-nav 5 --pct-majornav 5 --pct-syskeys 0 --pct-appswitch 20 --pct-flip 0 --pct-anyevent 0 -v -v -v "+str(run_times)
    monkey_command="monkey --throttle 500 -p com.dengtacj.stock --ignore-crashes --monitor-native-crashes --ignore-timeouts --ignore-native-crashes --pct-touch 25 --pct-motion 20 --pct-trackball 25 --pct-nav 5 --pct-majornav 5 --pct-syskeys 0 --pct-appswitch 20 --pct-flip 0 --pct-anyevent 0 -v -v -v "+str(runTimes)

    log_output(monkey_command)
    #计算top命令-n参数的值,即刷新多少次

    log_output("start run monkey and record mem & cpu")
    threads = []

    #开始执行获取cpu线程
    t1 = RecordThread("CPU",cpu_log_path,"adb -s "+device+" shell top -n 1 |grep 'com.dengtacj.stock\r'")
    
    #开始执行获取mem线程
    t2 = RecordThread("MEM", mem_log_path, "adb -s "+device+" shell procrank |grep 'com.dengtacj.stock\r' ")

    #开始执行monkey
    t3 = RecordThread("FPS", fps_log_path, 'adb shell dumpsys gfxinfo com.dengtacj.stock |sed -n -e "/Profile/,/hierarchy/p"')

    if MonkeyRun:
        t4=MonkeyThread("adb shell "+monkey_command)
        threads.append(t4)


    threads.append(t3)
    threads.append(t2)
    threads.append(t1)

    for t in threads:
        t.setDaemon(True)

    #开始执行所有线程
    for t in threads:
        t.start()

    time.sleep(runTime)


    # #等待所有线程结束
    for t in threads:
        t.stop()

    print "==============="
    log_output("finish run monkey and record mem & cpu")

def analyse_log():
    # tmp_path = config.outpath + config.sep + config.now_time + config.sep +"tmp"
    # if not os.path.exists(tmp_path):
    #    os.mkdir(tmp_path)

    # cpu_log_path='/Users/dengtacj/AutoTest/android-perform/out/20161025_165959/monitor_cpu.txt'
    # mem_log_path='/Users/dengtacj/AutoTest/android-perform/out/20161025_165959/monitor_mem.txt'
    # fps_log_path='/Users/dengtacj/AutoTest/android-perform/out/20161025_165959/monitor_fps.txt'

    cpu_dict=analysisCPU(cpu_log_path)
    mem_dict = analysisMEM(mem_log_path)
    fps_dict= analysisFPS(fps_log_path)

    generateHtml(cpu_dict,mem_dict,fps_dict)
    print "http://192.168.10.43:8082/out/"+now_time+"/report.html"

#
# def send_email(startTime,stopTime):
# 	#获取设备信息
#     model = get_model()
#     androidVersion = get_androidVersion()
#     cpuInfo = get_cpuInfo()
#     buildVersionIncremental = get_buildVersionIncremental()
#     buildDate = timestamp_datetime(float(get_buildDate()))
#     apkVersion=get_APKVersion()
#     msg = MIMEMultipart('related')
#     msg['Subject']=u"Dengta("+apkVersion+")--Android性能测试报告--测试设备:("+model+")"
#     msg['From']=config.me
#     msg['To']=';'.join(config.mailto_list)
#
#     content = ""
#     content+="<html>"
#     content+="<head>"
#     content+="<meta http-equiv=Content-Type content=\"text/html;charset=gb2312\">"
#     content+="<style type=\"text/css\">"
#     content+="body {font-family:\"" + "微软雅黑".decode('UTF-8').encode('GBK') + "\",\"宋体\",\"黑体\",Arial,Tahoma,Geneva,sans-serif;}"
#     content+="table {width:90%;border:2px solid;border-collapse:collapse;}"
#     content+="th {border-width:2px;border-style:solid;border-color:black;text-align:center;width:150px;background-color:#AEEEEE;color:red;}"
#     content+="td {border-width:2px;border-style:solid;}"
#     content+="</style>"
#     content+="</head>"
#     content+="<body>"
#     content+="<span><b>Dengta版本:".decode('UTF-8').encode('GBK') + str(apkVersion) + "</b><span>"
#     #content+="<body><table border='1'>"
#     #content+="<tr><td>Dengta版本</td><td>".decode('UTF-8').encode('GBK') + str(apkVersion) + "</td></tr></table>"
#     content += "<br/>"
#     content+="<span><b>运行时长(分):".decode('UTF-8').encode('GBK') + str(config.runTime) + "</b><span>"
#     content += "<br/>"
#     content+="<span><b>开始时间:".decode('UTF-8').encode('GBK') + startTime + "</b><span>"
#     content += "<br/>"
#     content+="<span><b>结束时间:".decode('UTF-8').encode('GBK') + stopTime + "</b><span>"
#     content += "<br/><br/>"
#     content+="<span><b>刷新次数:".decode('UTF-8').encode('GBK') + str(config.runTime * 60/config.updateTime) + "</b><span>"
#     content += "<br/>"
#     content+="<span><b>刷新频率(秒):".decode('UTF-8').encode('GBK') + str(config.updateTime) + "</b><span>"
#     content += "<br/>"
#     content+="<span><b>设备名称:".decode('UTF-8').encode('GBK') + str(model) + "</b><span>"
#     content += "<br/>"
#     content+="<span><b>系统版本:".decode('UTF-8').encode('GBK') + str(androidVersion) + "</b><span>"
#     #开始执行monke
#     content += "<br/>"
#     content+="<span><b>CPU信息:".decode('UTF-8').encode('GBK') + str(cpuInfo) + "</b><span>"
#     content += "<br/>"
#     content+="<span><b>系统编译增量:".decode('UTF-8').encode('GBK') + str(buildVersionIncremental) + "</b><span>"
#     content += "<br/>"
#     content+="<span><b>系统编译日期:".decode('UTF-8').encode('GBK') + str(buildDate) + "</b><span>"
#     content += "<br/>"
#
#     content += "<br/>"
#     content+="<span><b>名词解释:</b><span>".decode('UTF-8').encode('GBK')
#     content += "<br/>"
#     content+="<span><b>PSS:实际使用的物理内存</b><span>".decode('UTF-8').encode('GBK')
#     content += "<br/>"
#     content+="<span><b>USS:进程独自占用的物理内存</b><span>".decode('UTF-8').encode('GBK')
#     content += "<br/>"
#
#     content += "<br/>"
#     content+="<span><b>System性能趋势:</b><span>".decode('UTF-8').encode('GBK')
#     #content+="<span><b>" + system_maxminavg.decode('UTF-8').encode('GBK') + "</b><span>"
#     content += "<br/>"
#     content += "<img src=\"cid:cpu.png\" alt=\"cpu.png\">"
#     content += "<br/>"
#     content += "<br/>"
#
#     content += "<img src=\"cid:mem.png\" alt=\"mem.png\">"
#     content += "<br/>"
#     content += "<br/>"
#
#     content+="<span><b>灯塔趋势:</b><span>".decode('UTF-8').encode('GBK')
#     #content+="<span><b>" + system_maxminavg.decode('UTF-8').encode('GBK') + "</b><span>"
#     content += "<br/>"
#     content += "<img src=\"cid:cpu_trend.png\" alt=\"cpu_trend.png\">"
#     content += "<br/>"
#     content += "<br/>"
#
#     content += "<img src=\"cid:mem_trend.png\" alt=\"mem_trend.png\">"
#     content += "<br/>"
#     content += "<br/>"
#     content+="</body>"
#     content+="</html>"
#
#     msg.attach(MIMEText(content,_subtype='html',_charset='gb2312'))
#
#     fp = open(config.cpu_png_path,'rb')
#     img = MIMEImage(fp.read())
#     img.add_header('Content-ID',"cpu.png")
#     msg.attach(img)
#
#     fp = open(config.mem_png_path,'rb')
#     img = MIMEImage(fp.read())
#     img.add_header('Content-ID',"mem.png")
#     msg.attach(img)
#
#     fp = open(config.cpu_trend_path,'rb')
#     img = MIMEImage(fp.read())
#     img.add_header('Content-ID',"cpu_trend.png")
#     msg.attach(img)
#
#     fp = open(config.mem_trend_path,'rb')
#     img = MIMEImage(fp.read())
#     img.add_header('Content-ID',"mem_trend.png")
#     msg.attach(img)
#
#     try:
#         ott_mail=smtplib.SMTP()
#         ott_mail.connect(config.mailserver)
#         ott_mail.login(config.user, config.password)
#         ott_mail.sendmail(config.me,config.mailto_list,msg.as_string())
#         ott_mail.close()
#         print "sendEmail OK"
#         log_output("send Email ok")
#         return True
#     except Exception,e:
#         print e
#         print "sendEmail fail"
#         #log_output("send Email fail:"+e)
#         return False
#



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
    out=ssh2(ip,port,username,psw,"ls -t /data/android/history |grep -v dtv|head -1")
    apkfile=ssh2(ip,port,username,psw,"ls  -rt /data/android/history/"+out.strip().rstrip('\r')+" |head -1")
    log_output("download apk file:"+apkpath+apkfile)
    print "/data/android/history/"+out.strip().rstrip('\r')+"/"+apkfile
    remote_scp(ip,port,username,psw,"/data/android/history/"+out.strip().rstrip('\r')+"/"+apkfile.strip().rstrip('\r'),apkpath+apkfile.strip().rstrip('\r'))
    run_cmd("adb -s "+device+" install -r "+apkpath+apkfile.strip().rstrip('\r'))
    time.sleep(5)
    run_cmd("adb -s "+device+" shell am start -W com.dengtacj.stock/.main.MainActivity")
    time.sleep(1)
    run_cmd("adb -s "+device+" shell am force-stop com.dengtacj.stock")
    time.sleep(1)
    run_cmd("adb -s "+device+" shell am start -W com.dengtacj.stock/.main.MainActivity")


if __name__=='__main__':
    if len(sys.argv)!=2:
        print "please give right arg:device"
        sys.exit(0)
    else:
        device=sys.argv[1]

    #环境准备
    env_prepare()
    
    #获取最新的apk
    # donwloadNewPackage()


    #记录cpu，mem
    startTime=getTime(1)
    run_record()
    stopTime=getTime(1)
    
    #分析日志
    analyse_log()

#startTime="2016-04-13 10:59:51"
#    stopTime="2016-04-13 12:31:44"

    #发送邮件
     send_email(startTime,stopTime)

