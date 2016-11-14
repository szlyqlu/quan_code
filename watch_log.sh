#!/bin/bash
#this is a test for watch log
#created at Fri Oct 14 13:37:12 JST 2016

if [ $# -lt 1 ];then
	echo "Usage:`basename $0` [LOGDIR_PATH] [option|PPID]"
	exit 1
fi

logdir=$1
_PPID=$2
log_key="expect -f"
html_dir="./`date +%Y%m%d`"
html_tempfile="./$html_dir/watch_log.`date +%Y%m%d%H%M%S`.html"

if [ -z $_PPID ];then
	log_count=`ps -ef|grep -v grep|grep "$log_key"|wc -l`
else
	log_count=`ps -ef|grep -v grep|grep "$log_key"|grep $_PPID|wc -l`
fi

if [ $log_count -eq 0 ];then
	echo "No new expect process.end"
	exit 0
fi

echo "=================================================="
echo "LOGDIR is [$logdir]."
echo "NEWLOG is [$log_count]."
read -p "Input the number of line you want to watch : " line_num

if [ -s $line_num ];then
	line_num=10
fi

[ -d $html_dir ] || mkdir $html_dir

echo "<html>">>$html_tempfile
echo "<body>">>$html_tempfile
echo "<h1 style=\"font-size:20px;color:green\">WATCH AT `date`</h1>">>$html_tempfile
num_count=1
for i in `ls -t $logdir|grep ".log$"|tr " " "\n"|head -$log_count`
do
	echo "">>$html_tempfile
	hostname=`echo $i|cut -d'.' -f1`
	echo "<a href=\"#\" id=\"test$num_count\" onclick=\"show('show$num_count')\">$hostname</a>">>$html_tempfile
	echo "    <p id=\"show$num_count\">">>$html_tempfile
	if [ $line_num -gt 1 ];then
		cat $logdir/$i|tail -$line_num|while read LINE
		do
		echo "${LINE}</br>">>$html_tempfile
		done
		echo "`cat $logdir/$i|tail -1`</br>">>$html_tempfile
		echo "</p></br>">>$html_tempfile
	else
		echo "`cat $logdir/$i|tail -$line_num`</br>">>$html_tempfile
		echo "</p></br>">>$html_tempfile
	fi
num_count=`expr $num_count + 1`
done

echo "</body>">>$html_tempfile
echo "<script>">>$html_tempfile
echo "    function show(id){">>$html_tempfile
echo "        var p = document.getElementById(id);">>$html_tempfile
echo "        if (p.style.display == 'none') {">>$html_tempfile
echo "        p.style.display = '';">>$html_tempfile
echo "        }">>$html_tempfile
echo "        else {">>$html_tempfile
echo "            p.style.display = 'none';">>$html_tempfile
echo "        }">>$html_tempfile
echo "    }">>$html_tempfile
echo "</script>">>$html_tempfile
echo "</html>">>$html_tempfile

firefox $html_tempfile
