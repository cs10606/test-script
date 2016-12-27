a=`adb devices|grep -c "device"`
if [ $a != 2 ];then
    echo "no device connect,please check"
    exit -1
fi


pid=`adb shell ps|grep "com.dengtacj.stock\r" |awk '{print $2}'`
echo "pid:"$pid

uid=`adb shell cat /proc/$pid/status |grep Uid |awk '{print $2}'`
echo "uid:"$uid


echo "receive network flow (B):======="
echo "adb shell cat /proc/uid_stat/$uid/tcp_rcv"
adb shell cat /proc/uid_stat/$uid/tcp_rcv

echo "send network flow(B):========"
adb shell cat /proc/uid_stat/$uid/tcp_snd

