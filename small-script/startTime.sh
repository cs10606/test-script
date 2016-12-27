#!/bin/bash

echo "force-time" >>time.txt
for((i=1;i<20;i++))
do
echo $i
adb shell am force-stop com.dengtacj.stock
sleep 5
adb shell am start -W com.dengtacj.stock/.main.MainActivity |grep WaitTime >>time.txt
sleep 2
done


echo "home" >>time.txt
for((i=1;i<20;i++))
do
echo $i
adb shell input keyevent 3
sleep 3
adb shell am start -W com.dengtacj.stock/.main.MainActivity |grep WaitTime >>time.txt
sleep 2
done

