
#添加备注到comments.csv
comment(){
if [ ! -f $testresult/comments.csv ];then
    echo "Date,Error Type,Log Name" >$testresult/comments.csv
fi
echo "`date +%m-%d" "%H":"%M":"%S`,$1,$2" >>$testresult/comments.csv
echo $1
}

#锁屏函数$1:0--lock;1--unlock；按显示内容判定处理，显示壁纸并且无其他activity则滑屏；黑屏则电源键唤醒加滑屏。
lock(){
local tmp=`wm size|busybox awk '{print $NF}'`
local x=`echo $tmp|busybox awk -F "x" '{print $1}'`
local y=`echo $tmp|busybox awk -F "x" '{print $2}'`
while true;do
    case `dumpsys SurfaceFlinger|grep "|....|"|busybox awk 'BEGIN{r="o"}{if($NF=="com.android.systemui.ImageWallpaper"||$NF=="com.android.systemui.keyguard.leui.KeyguardImageWallpaper")r="l"}END{print NR-1 r}'` in
        "1o")
            local state=0
        ;;
        "3l")
            local state=1
        ;;
        *)
            local state=2
        ;;
    esac
    case $1 in
        0)
            if [ $state -ne 0 ];then
                input keyevent 26
            else
                break
            fi
            sleep 1
        ;;
        1)
            if [ $state -eq 0 ];then
                input keyevent 26&&sleep 1&&input swipe $((x/2)) $((4*y/5)) $((x/2)) $((y/5))
            elif [ $state -eq 1 ];then
                input swipe $((x/2)) $((4*y/5)) $((x/2)) $((y/5))
            else
                break
            fi
            sleep 1
        ;;
    esac
done
}

#筛查指定log文件的函数
output_error(){
if [ -f $1 ];then
    local times1=`grep -c "ANR in" $1`
    anr=$((anr+times1))
#local times2=`grep -c "FATAL EXCEPTION" $1`
    local times2=`grep -c -i "handleException run" $1`
    fatal=$((fatal+times2))
    #local times3=`grep -c "Build fingerprint" $1`
    #fingerprint=$((fingerprint+times3))
    local times4=`grep -c "OutOfMemoryError" $1`
    oom=$((oom+times4))

    #if [ $times1 -ne 0 -o $times2 -ne 0 -o $times3 -ne 0 -o $times4 -ne 0 ];then
    if [ $times1 -ne 0 -o $times2 -ne 0  -o $times4 -ne 0 ];then
        if [ ! -d $testresult/log ];then
            mkdir $testresult/log
        fi
        time_name="`date +%Y%m%d%H%M%S`"
        busybox mv $1 $testresult/log/$time_name.log
        #bugreport >$testresult/log/$time_name.bugreport
        screencap $testresult/log/$time_name.png
        local result="Error:"
        if [ $times1 -ne 0 -a ! -z "`ls /data/anr 2>/dev/null`" ];then
            mkdir $testresult/log/$time_name
            mv /data/anr/* $testresult/log/$time_name/
            local result=$result"ANR;"
        fi
        if [ $times2 -ne 0 ];then
            if [ ! -d $testresult/log/$time_name ];then
                mkdir $testresult/log/$time_name
            fi
            cat /sdcard/Android/data/com.dengtacj.stock/files/log/com.dengtacj.stock_crash.log > $testresult/${time_name}_crash.log
            local result=$result"CRASH;"
        fi
        #if [ $times3 -ne 0 -a ! -z "`ls /data/tombstones 2>/dev/null`" ];then
        #    if [ ! -d $testresult/log/$time_name ];then
        #        mkdir $testresult/log/$time_name
        #    fi
        #    mv /data/tombstones/* $testresult/log/$time_name
        #    local result=$result"tombstones;"
        #fi
        if [ $times4 -ne 0 ];then
            local result=$result"OOM;"
        fi
        comment "$result" "$time_name.log"
    else
        rm $1
    fi
fi
}

#创建$log_f函数，
c_log(){
if [ -f $log_f ];then
    while true;do
        if [ -f $testresult/check_error.log ];then
            sleep 1
        else
            break
        fi
    done
    local p=`busybox ps`
    kill -9 `echo "$p"|grep "logcat -f $log_f -v time"|busybox awk '{print $1}'`
    busybox mv $log_f $testresult/check_error.log
fi
if [ $1 -eq 0 ];then
    logcat -c
    logcat -f $log_f -v time &
fi
if [ -f $testresult/check_error.log ];then
    output_error $testresult/check_error.log
    echo -e "local mac=$mac
build id=$build
ANR=$anr
CRASH=$fatal
OOM=$oom" >$testresult/statistics.txt
fi
}

#可用空间少于80%，删除ledown下载的视频文件
clear_files(){
echo "====clear files"
if [ `busybox df /sdcard|busybox awk '{r=substr($(NF-1),1,length($(NF-1))-1)}END{print r+0}'` -ge 80 ];then
    rm /sdcard/ledown/*
fi
}


#Global variables
anr=0
fatal=0
#fingerprint=0
oom=0
log_f="/data/check_error.log"
if [ -f $log_f ];then
    rm $log_f
fi
testresult="/data/monkey"
if [ -d $testresult ];then
    rm -r $testresult
fi
mkdir $testresult
mac=`cat /sys/class/net/*/address|busybox sed -n '1p'|busybox tr -d ':'`
build=`getprop ro.build.fingerprint`
if [ -z $build ];then
    build=`getprop ro.build.description`
fi

#等待monkey进程执行完毕函数，如果锁屏则自动解锁
waitmonkey(){
echo "====wait monkey"
local a=0
while [ $a != 1 ];do
    local a=`/system/bin/ps |grep -c "com.android.commands.monkey"`
done
while [ $a != 0 ];do
    c_log 0
    lock 1
    #clear_files
    sleep 10
    local a=`/system/bin/ps |grep -c "com.android.commands.monkey"`
done
c_log 1
}

#等待指定时间，间隔10S筛查log
wait_time(){
local chek_begin=`busybox awk -F. 'NR==1{print $1}' /proc/uptime`
local check=$chek_begin
c_log 0
while true;do
    local chek_end=`busybox awk -F. 'NR==1{print $1}' /proc/uptime`
    if [ $((chek_end-chek_begin)) -ge $1 ];then
       # clear_files
        c_log 1
        break
    elif [ $((chek_end-check)) -gt 10 ];then
        local check=$chek_end
       # clear_files
        c_log 0
    else
        sleep 1
    fi
done
}

busybox pkill monkey
#以下为monkey脚本逻辑

#如锁屏先解锁
lock 1
#记录开始时间
comment "package" "start test"
echo $1
#-p package限定执行范围自行调整；事件间隔一般手机500ms；事件比例按测试目的配置；事件数按时常预估情况设定，此情况25000在1小时左右；
monkey -p com.dengtacj.stock --throttle 500 --ignore-crashes --monitor-native-crashes --ignore-timeouts --ignore-native-crashes --pct-touch 20 --pct-trackball 30 --pct-motion 15 --pct-appswitch 30 --pct-anyevent 5 -v -v -v $1 1>>$testresult/monkey.log 2>&1 &
#等待结束
waitmonkey
#记录结束时间
comment "com.dengtacj.stock"
#锁屏静置十分钟，自己设定的，下一条前让手机休息下，并且可通过cpu内存监控关注停止monkey后内存是否持续上涨。
lock 0
comment "lock" "lock screen"
wait_time 6
comment "wait_time" "finish wait 600"

#下一条monkey语句

#记录测试结束
comment "finish" "END"
#通知停止监控
echo "`date +%m-%d" "%H":"%M":"%S` stop MCM" > /data/local/tmp/stop