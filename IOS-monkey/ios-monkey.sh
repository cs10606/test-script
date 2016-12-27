#!/bin/sh
. /etc/profile
. ~/.bash_profile
source /Users/dengtacj/.bash_profile

#5(8.1) 074BF513-F19C-424D-A35C-DB57016E0047
#zhenji touch5(9.3.2)  f9b2f389f7b5c359b14ec637306412bb69facdfe
#shiyang 252e718784938e47fc906b70f1ec482784855812
#device=f9b2f389f7b5c359b14ec637306412bb69facdfe
#device=dafa276989802b3a29cc796beb3305afa460eb3b
#times=18000
#count=3


if [ $# != 3 ];then
    echo "pleace give right arg:device,times,count"
    exit 0
fi

device=$1
times=$2
count=$3
echo "device : "$device
echo "times : "$times
echo "count : "$count

ios_project=/Users/dengtacj/ios

#cur_dir=$(pwd)
cur_dir=$(cd `dirname $0`;pwd)

log(){
echo $* >>$cur_dir/log.txt
echo $*
}

if [ ! -d $cur_dir/symbol ];then
    mkdir $cur_dir/symbol
fi

if [ ! -d $cur_dir/ipa ];then
    mkdir $cur_dir/ipa
fi

#build
build_time=`date +%Y%m%d_%H%M%S`

log "get new code"
cd $ios_project/WorkSpace
git reset --hard
git pull
sed -i -e 's|shellScript\ =\ \"\.\/Fabric\.framework\/run|shellScript\ =\ \"\#\./Fabric\.framework\/run|' ../Stock/stock.xcodeproj/project.pbxproj
#sed -i -e 's|PRODUCT_BUNDLE_IDENTIFIER\ =\ com\.wedengta\.stock|PRODUCT_BUNDLE_IDENTIFIER\ =\ com\.wedengta\.inhouse\.stock|' ../Stock/stock.xcodeproj/project.pbxproj
#sed -i -e 's|PRODUCT_BUNDLE_IDENTIFIER\ =\(.*\)|PRODUCT_BUNDLE_IDENTIFIER\ =\ com\.wedengta\.stock\;|' ../Stock/stock.xcodeproj/project.pbxproj
#sed -i -e 's|buildConfiguration\ =\(.*\)|buildConfiguration\ =\ \"AppStore\"|' ../Stock/stock.xcodeproj/xcshareddata/xcschemes/Stock.xcscheme
#sed -i -e  "122s|buildConfiguration\ =\(.*\)|buildConfiguration\ =\ \"AppStore\"|" ../Stock/stock.xcodeproj/xcshareddata/xcschemes/Stock.xcscheme
sed -i -e 's|DTS_BUNDLE_IDENTIFIER\ =\(.*\)|DTS_BUNDLE_IDENTIFIER\ =\ com\.wedengta\.stock\;|' ../Stock/stock.xcodeproj/project.pbxproj
security unlock-keychain -p " " ${HOME}/Library/Keychains/login.keychain
#xcodebuild -workspace Stock.xcworkspace  -scheme  Stock -sdk iphoneos CODE_SIGN_IDENTITY="iPhone Distribution: DengTa Financial Information Co., Ltd." PROVISIONING_PROFILE=""  -configuration Debug clean build  2>&1 > /Users/dengtacj/build/build.log
xcodebuild -workspace Stock.xcworkspace  -scheme  Stock -sdk iphoneos CODE_SIGN_IDENTITY="iPhone Developer" PROVISIONING_PROFILE="7a5ffe90-dc56-4509-be54-af891be25678" DevelopmentTeam="H9EQ65PL9Q" EXPANDED_CODE_SIGN_IDENTITY="BB7268147047B3EB5B13C22848847617D994E530" EXPANDED_CODE_SIGN_IDENTITY_NAME="iPhone Developer: shuning tian (L643X9USNF)"  -configuration Debug clean build

#xcodebuild -workspace Stock.xcworkspace  -scheme  Stock -sdk iphoneos CODE_SIGN_IDENTITY="iPhone Developer" PROVISIONING_PROFILE="7a5ffe90-dc56-4509-be54-af891be25678" DevelopmentTeam="H9EQ65PL9Q" EXPANDED_CODE_SIGN_IDENTITY="BB7268147047B3EB5B13C22848847617D994E530" EXPANDED_CODE_SIGN_IDENTITY_NAME="iPhone Developer: shuning tian (L643X9USNF)"  -configuration Debug clean build AppStore  2>&1 > /Users/dengtacj/ios-monkey/build.log

if [[ $? == 0 ]]; then

log "build Success------------------------------------------------"
filePath=$cur_dir/ipa/Stock_${build_time}.ipa
xcrun -sdk iphoneos PackageApplication  -v /Users/dengtacj/Library/Developer/Xcode/DerivedData/Stock-cdaemnqcgwohjwgfavgfdulvmhhq/Build/Products/Debug-iphoneos/Stock.app  -o $filePath
mkdir $cur_dir/symbol/${build_time}
cp -r /Users/dengtacj/Library/Developer/Xcode/DerivedData/Stock-cdaemnqcgwohjwgfavgfdulvmhhq/Build/Products/Debug-iphoneos/Stock.app.dSYM $cur_dir/symbol/${build_time}/Stock.app.dSYM
cp -r /Users/dengtacj/Library/Developer/Xcode/DerivedData/Stock-cdaemnqcgwohjwgfavgfdulvmhhq/Build/Products/Debug-iphoneos/Stock.app $cur_dir/symbol/${build_time}/Stock.app
#curl -F "file=@$filePath" -F "uKey=$uKey" -F "_api_key=$apiKey" http://www.pgyer.com/apiv1/app/upload

log "install new package"
/Users/dengtacj/fruitstrap/fruitstrap -b $filePath

else
log "build failed "
fi


echo $cur_dir
cd $cur_dir


time_name="`date +%Y%m%d_%H%M%S`"
log ""
log "Start at :"$time_name
log "monkey times :"$times

if [ ! -d $cur_dir/log ];then
    mkdir $cur_dir/log
fi


symbol_folder=`ls $cur_dir/symbol|tail -1`



log "Start at:"`date +%Y-%m-%d-%H:%M:%S`
log "smart_monkey -a com.wedengta.stock -w $device  -d $cur_dir/log -t $times -n $count --detail-count 150 -s $cur_dir/symbol/$symbol_folder/Stock.app.dSYM"
smart_monkey -a com.wedengta.stock -w $device  -d $cur_dir/log -t $times -n $count --detail-count 150 -s $cur_dir/symbol/$symbol_folder/Stock.app.dSYM
log "finish at:"`date +%Y-%m-%d-%H:%M:%S`


folder=`ls $cur_dir/log|tail -1`

day_name="`date +%Y%m%d`"
if [[ $folder =~ $day_name ]];then
log "result folder:"$folder
else
log "not run ,result folder:"
python $cur_dir/send.py "" "" "" "one"
exit 0
fi

#url=http://192.168.9.89:8080/$folder/index.html
url=http://192.168.10.43:8080/

log "result url :"$url
log "result file:"$cur_dir/log/$folder/index.html

if [ ! -f $cur_dir/log/$folder/index.html ];then
log "not found result file ,please check!!!"
exit 0
fi

a=`cat $cur_dir/log/$folder/index.html |grep Results |awk -F ', ' '{print $3}'|awk -F ' ' '{print $1}'`
log "crash num :"$a
if [ $a != 0 ];then
user="all"
else
user="one"
fi

#user="one"

#sendemail
log "send email"

#python $cur_dir/sendEmail.py $url $user
python $cur_dir/send.py $cur_dir/log/ $url $folder $user

#adb shell dumpsys gfxinfo com.dengtacj.stock >1.txt
