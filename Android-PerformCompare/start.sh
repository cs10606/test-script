#!/bin/sh

source /Users/dengtacj/.bash_profile
device=5655d3d5
echo $PATH
adb -s $device reboot
sleep 120

a=`adb devices|grep -c "device"`
if [ $a != 2 ];then
sleep 60
fi

adb -s $device root
sleep 10

pyenv global system
python -V
#python /Users/dengtacj/Documents/monkey/new/system_v1/system.py
python /Users/dengtacj/AutoTest/android-performCompare/system.py $device
pyenv global 3.5.2