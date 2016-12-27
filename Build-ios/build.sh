#!/bin/bash
source /Users/dengtacj/.bash_profile
build_time=`date +%Y%m%d_%H%M%S`
uKey=b705f1aa8e1b512997ae1203d7fa9e3b
apiKey=f3eb70f2742b2b2e123672f9ce942f17
ios_project=/Users/dengtacj/ios
cur_dir=$(cd `dirname $0`;pwd)

echo $cur_dir


cd $ios_project/WorkSpace
git reset --hard
git pull
sed -i -e 's|shellScript\ =\ \"\.\/Fabric\.framework\/run|shellScript\ =\ \"\#\./Fabric\.framework\/run|' ../Stock/stock.xcodeproj/project.pbxproj
sed -i -e 's|PRODUCT_BUNDLE_IDENTIFIER\ =\(.*\)|PRODUCT_BUNDLE_IDENTIFIER\ =\ com\.wedengta\.inhouse\.stock;|' ../Stock/stock.xcodeproj/project.pbxproj
sed -i -e 's|jsCodeLocation\ =\(.*\)|jsCodeLocation\ =\ [[NSBundle mainBundle] URLForResource:@"index.ios" withExtension:@"jsbundle"];|' ../Stock/Stock/Modules/RN/UIViewController/DTSRNBaseVC.m
security unlock-keychain -p " " ${HOME}/Library/Keychains/login.keychain

cd $ios_project/ReactComponent 
#curl http://localhost:8081/index.ios.bundle -o index.ios.jsbundle
react-native bundle --entry-file  index.ios.js --bundle-output ./index.ios.jsbundle --platform ios  --dev false
cp -rf $ios_project/ReactComponent/index.ios.jsbundle $ios_project/Stock/Stock/Resource/ReactNative/index.ios.jsbundle 

cd $ios_project/WorkSpace
xcodebuild -workspace Stock.xcworkspace  -scheme  Stock -sdk iphoneos CODE_SIGN_IDENTITY="iPhone Distribution: DengTa Financial Information Co., Ltd." PROVISIONING_PROFILE=""  -configuration Debug clean build 
#xcodebuild -workspace Stock.xcworkspace  -scheme  Stock -sdk iphoneos CODE_SIGN_IDENTITY="iPhone Developer"  -configuration "Release Adhoc" clean build  2>&1 > /Users/dengtacj/build/build.log
#xcodebuild -workspace Stock.xcworkspace  -scheme  Stock -sdk iphoneos CODE_SIGN_IDENTITY="iPhone Distribution: DengTa Financial Information Co., Ltd. (H9EQ65PL9Q)"  -configuration Debug clean build 
if [[ $? == 0 ]]; then

     echo "Success------------------------------------------------"
	mkdir -p $cur_dir/ipa
       filePath=$cur_dir/ipa/Stock_${build_time}.ipa
       xcrun -sdk iphoneos PackageApplication  -v /Users/dengtacj/Library/Developer/Xcode/DerivedData/Stock-cdaemnqcgwohjwgfavgfdulvmhhq/Build/Products/Debug-iphoneos/Stock.app  -o $filePath 
       mkdir -p $cur_dir/symbol/${build_time}
       cp -r /Users/dengtacj/Library/Developer/Xcode/DerivedData/Stock-cdaemnqcgwohjwgfavgfdulvmhhq/Build/Products/Debug-iphoneos/Stock.app.dSYM $cur_dir/symbol/${build_time}/Stock.app.dSYM
       cp -r /Users/dengtacj/Library/Developer/Xcode/DerivedData/Stock-cdaemnqcgwohjwgfavgfdulvmhhq/Build/Products/Debug-iphoneos/Stock.app $cur_dir/symbol/${build_time}/Stock.app
       echo "curl -F file=@$filePath -F uKey=$uKey -F _api_key=$apiKey http://www.pgyer.com/apiv1/app/upload"
       curl -F "file=@$filePath" -F "uKey=$uKey" -F "_api_key=$apiKey" http://www.pgyer.com/apiv1/app/upload
        echo "build successfully"

else
       echo "Failed-------------------------------------------------"
       echo "build failed "
fi

#if test -s /Users/mac-build/Library/Developer/Xcode/DerivedData/Stock-chykcubcbbcisodueduuuyhdmqdq/Build/Products/Debug-iphoneos/Stock.app.dSYM
#then
#	filePath=/Users/mac-build/build/ipa/Stock_${build_time}.ipa
#	xcrun -sdk iphoneos PackageApplication  -v /Users/mac-build/Library/Developer/Xcode/DerivedData/Stock-chykcubcbbcisodueduuuyhdmqdq/Build/Products/Debug-iphoneos/Stock.app -o $filePath
#	mkdir /Users/mac-build/build/symbol/${build_time}
#	cp -r /Users/mac-build/Library/Developer/Xcode/DerivedData/Stock-chykcubcbbcisodueduuuyhdmqdq/Build/Products/Debug-iphoneos/Stock.app.dSYM /Users/mac-build/build/symbol/${build_time}/Stock.app.dSYM
#	cp -r /Users/mac-build/Library/Developer/Xcode/DerivedData/Stock-chykcubcbbcisodueduuuyhdmqdq/Build/Products/Debug-iphoneos/Stock.app /Users/mac-build/build/symbol/${build_time}/Stock.app
#	curl -F "file=@$filePath" -F "uKey=$uKey" -F "_api_key=$apiKey" http://www.pgyer.com/apiv1/app/upload
#        echo "build successfully"
#
#else
#	echo "build failed "
#fi
