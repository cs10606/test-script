#!/bin/sh

source /Users/dengtacj/.bash_profile

if [ $# == 0 ];then
    echo "pleace give device name!"
    exit 0
fi

device=$1
if [ $# == 2 ];then
    times=$[$2*25000]
else
    times=75000
fi

echo "device name :"$device
echo "excute time:"$times


echo "start"
adb -s $device reboot
sleep 60

a=`adb devices|grep -c "device"`
if [ $a != 2 ];then
sleep 60
fi

adb -s $device root
sleep 10

cur_dir=$(cd `dirname $0`; pwd)
echo $cur_dir


log(){
echo $* >>$cur_dir/log.txt
echo $*
}


time_name="`date +%Y%m%d_%H%M%S`"
log ""
log "Start at :"$time_name
log "monkey times :"$times

if [ ! -d $cur_dir/log ];then
    mkdir $cur_dir/log
fi

mkdir $cur_dir/log/$time_name

#check devices
a=`adb devices|grep -c "device"`
if [ $a != 2 ];then
    log "Connected devices are wrong"
    log `adb devices`
fi

#get new apk
if [ ! -d $cur_dir/apk ];then
    mkdir $cur_dir/apk
fi
datenew=`ssh -p 36000 devbase@192.168.9.26 "ls -t /data/android/history |grep -v dtv |head -1"`
apkfile=`ssh -p 36000 devbase@192.168.9.26 "ls -S /data/android/history/$datenew |grep release |head -1"`

if [ ${apkfile:0-3} = apk ];then
    scp -P 36000 devbase@192.168.9.26:/data/android/history/$datenew/$apkfile $cur_dir/apk
    log "download apk:"$apkfile

    #install and skip start pic
    log "install new apk"
    adb -s $device install -r $cur_dir/apk/$apkfile
fi


adb -s $device shell am start -W com.dengtacj.stock/.main.MainActivity
adb -s $device shell am force-stop com.dengtacj.stock

#run adb monkey
log "adb root"
adb -s $device root
adb -s $device push $cur_dir/monkey_mobile.sh /data/
adb -s $device shell chmod 777 /data/monkey_mobile.sh

log "start monkey in mobile"
#python $cur_dir/CountFPS.py $times/2
adb -s $device shell /data/monkey_mobile.sh $times

#get log
log "get monkey log"
adb -s $device pull /data/monkey $cur_dir/log/$time_name/

crashlog=`adb shell ls /sdcard/Android/data/com.dengtacj.stock/files/log/ | grep "crash"`
if [[ $crashlog = "" ]];then
log "no crash log"
else
log "have crash log,get crash log"
adb -s $device pull /sdcard/Android/data/com.dengtacj.stock/files/log/$crashlog $cur_dir/log/$time_name/
fi

#zip
if [ ! -d $cur_dir/zip ];then
    mkdir $cur_dir/zip
fi

log "zip log"
cd $cur_dir/log
zip -r $cur_dir/zip/$time_name.zip $time_name

commentfile=$cur_dir/log/$time_name/comments.csv
flag=`cat $commentfile |grep 'Error:'`
log "commentfile $commentfile"

if [[ $flag = "" ]];then
user='one'
else
user='all'
fi

#user='one'

#sendemail
log "send email"
pyenv global 3.5.2
#python $cur_dir/sendEmail.py $cur_dir/zip/$time_name.zip $user
python $cur_dir/sendEmail_NEW.py $cur_dir/zip/$time_name.zip $user $cur_dir/log/$time_name
#adb shell dumpsys gfxinfo com.dengtacj.stock >1.txt
