
WORKDIR=$(cd "$(dirname "$0")"; pwd)
BINDIR="$WORKDIR/bin"

build_time=`date +%Y%m%d_%H%M%S`

device=f9b2f389f7b5c359b14ec637306412bb69facdfe
#device=b8db6510979fad0495fb65cd578d6c14029da259
#app=com.wedengta.stock.reserve
app=com.wedengta.stock
script=$WORKDIR/scripts/New.js
#script=$WORKDIR/scripts/UIAutoMonkey.js
template=$WORKDIR/templates/Automation_Monitor_CoreAnimation_Energy_Network.tracetemplate
result_path=$WORKDIR/log/$build_time



pyenv global system
python -V
echo "$BINDIR/automation.sh -s $device -t $template -c $script -o $result_path $app"
$BINDIR/automation.sh -s "$device" -t "$template" -c "$script" -o "$result_path" "$app"
# $BINDIR/automation.sh -s "$device" -t "$template" -c "$script" -d "$dsym_path" -o "$result_path" "$app"

if [ -f $result_path/report.html ];then
    echo "find result html"

    echo $result_path
    echo $WORKDIR
#    result=`echo $result_path | sed 's#\/#\\\/#g'`
#    work=`echo $WORKDIR | sed 's#\/#\\\/#g'`

#    echo ${result}
#    echo ${work}

#    sed -i "" "s/${result}/./g" $result_path/report.html
#    sed -i "" "s/${work}/..\/../g" $result_path/report.html
else
    echo "not found html"
fi

echo "html url: "
echo "http://192.168.10.43:8081/log/$build_time/report.html"
pyenv global 3.5.2