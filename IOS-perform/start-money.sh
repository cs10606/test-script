
WORKDIR=$(cd "$(dirname "$0")"; pwd)
BINDIR="$WORKDIR/bin"

build_time=`date +%Y%m%d_%H%M%S`

#device=252e718784938e47fc906b70f1ec482784855812
device=f9b2f389f7b5c359b14ec637306412bb69facdfe
app=com.wedengta.stock
script=$WORKDIR/scripts/UIAutoMonkey.js
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
    result=`echo $result_path | sed 's#\/#\\\/#g'`
    work=`echo $WORKDIR | sed 's#\/#\\\/#g'`

    echo ${result}
    echo ${work}

    sed -i "" "s/${result}/./g" $result_path/report.html
    sed -i "" "s/${work}/..\/../g" $result_path/report.html
else
    echo "not found html"
fi

echo "html url: "
echo "http://192.168.10.43:8081/log/$build_time/report.html"

pyenv global 3.5.2