
#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import datetime
import os,sys


def getTime(type):
    now = datetime.datetime.now()
    if type ==1:
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif type ==0:
        return now.strftime("%Y%m%d_%H%M%S")

#运行时长,以分钟为单位
runTime=120

#刷新间隔,默认为10秒
updateTime=10

#过滤进程名
#com.tencent.portfolio
#com.xueqiu.android
#com.hexin.plat.android
#com.upchina
#com.eastmoney.android.berlin

packageNameList=["com.dengtacj.stock","com.tencent.portfolio","com.xueqiu.android","com.hexin.plat.android","com.upchina"]

packageNameDict={"com.dengtacj.stock":"灯塔","com.tencent.portfolio":"自选股","com.xueqiu.android":"雪球","com.hexin.plat.android":"同花顺","com.upchina":"优品"}

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

#日志路径
logpath = path + sep + "log.txt"

#输出目录
outpath = path + sep + "out"

#历史目录
historypath = path + sep + "history"
historyfile = historypath + sep +"history.txt"

#apk目录
apkpath = path + sep + "apk" +sep

#远程登录信息
ip="192.168.9.26"
port=36000
username="devbase"
psw="devbase"

cpu_log_path = outpath + sep + now_time + sep + "monitor_cpu.txt"     #cpu日志文件
mem_log_path = outpath + sep + now_time + sep + "monitor_mem.txt"     #mem日志文件

cpu_png_path = outpath + sep + now_time + sep + "cpu.png"     #cpu曲线图
mem_png_path = outpath + sep + now_time + sep + "mem.png"     #mem曲线图

cpu_trend_path = outpath + sep + now_time + sep + "cpu_trend.png"     #cpu曲线图
mem_trend_path = outpath + sep + now_time + sep + "mem_trend.png"     #mem曲线图

# cpu_log_path = outpath + sep + now_time + sep + "monitor_cpu.txt"     #cpu日志文件
# mem_log_path = outpath + sep + now_time + sep + "monitor_mem.txt"     #mem日志文件
#
# cpu_png_path = '/Users/dengtacj/AutoTest/android-performCompare/out/20161218_010311/cpu.png'     #cpu曲线图
# mem_png_path = '/Users/dengtacj/AutoTest/android-performCompare/out/20161218_010311/mem.png'     #mem曲线图
#
# cpu_trend_path = '/Users/dengtacj/AutoTest/android-performCompare/out/20161218_010311/cpu_trend.png'     #cpu曲线图
# mem_trend_path = '/Users/dengtacj/AutoTest/android-performCompare/out/20161218_010311/mem_trend.png'     #mem曲线图