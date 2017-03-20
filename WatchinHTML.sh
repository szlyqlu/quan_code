#!/bin/bash
# create at Tue Mar 14 2017

#Parameter defined
html_dir="./`date +%Y%m%d`"
html_tempfile="./$html_dir/watch_log.`date +%Y%m%d%H%M%S`.html"
#Parameter defined

usage_error () {
    echo "Usage:`basename $0` [-d dir] [-n filenum|-p ppid] [-t linenum|-o \"startline:endline\"]"
}

ppid_ck () {
local _PPID=$1
local log_key="expect -f"
log_count=`ps -ef|grep -v grep|grep "$log_key"|grep $_PPID|wc -l`
return $log_count
}

write_html () {
local html_file=$1
local log_flags=$2
local get_flags=$3
#html head
echo "<html>">>$html_file
echo "<body>">>$html_file
echo "<h1 style=\"font-size:20px;color:green\">WATCH AT `date`</h1>">>$html_file
#html head

case $log_flags in
    "DIR")
	if [ $log_count ];then
            TARGET=`ls -t $logdir|grep ".log$"|tr " " "\n"|head -$log_count`
	    write_button $log_count
	else
	    TARGET=`ls -t $logdir|grep ".log$"|tr " " "\n"|head -$filenum`
	    write_button $filenum
	fi
	case $get_flags in
	    "_TAIL")
		num_count=1
		for f in $TARGET
		do
		    hostname=`echo $f|cut -d'.' -f1`
		    echo "<a href=\"##\" id=\"test$num_count\" onclick=\"show('show$num_count')\">$hostname</a>">>$html_file
		    echo "    <pre id=\"show$num_count\">">>$html_file
		    cat $logdir/$f|tail -$linenum|col -b|sed 's/1m31m//g;s/# Bm/# /g'|sed 's:\?1034h::g'|sed 's/\(.*\)0m00m\(.*\)0m\(.*\)/\1\2/g'>>$html_file
		    echo "</pre></br>">>$html_file
		    num_count=`expr $num_count + 1`
		done
		;;
	    "_SED")
		num_count=1
		for f in $TARGET
		do
		    hostname=`echo $f|cut -d'.' -f1`
		    echo "<a href=\"##\" id=\"test$num_count\" onclick=\"show('show$num_count')\">$hostname</a>">>$html_file
		    echo "    <pre id=\"show$num_count\">">>$html_file
		    sed -n "/$s_word/,/$e_word/"p $logdir/$f|col -b|sed 's/1m31m//g;s/# Bm/# /g'|sed 's:\?1034h::g'|sed 's/\(.*\)0m00m\(.*\)0m\(.*\)/\1\2/g'>>$html_file
		    echo "</pre></br>">>$html_file
		    num_count=`expr $num_count + 1`
		done
		;;
	esac
	;;
esac
}
write_button () {
local endcount=$1
i=1
while [ $i -le $endcount ]
do
   if [ -z $section_num ];then
	section_num="show('show$i')"
   else
	section_num="$section_num,show('show$i')"
   fi
   i=`expr $i + 1`
done

echo "<button type=\"button\" onclick=\"$section_num\">show/hide all</button></br></br>">>$html_tempfile
}

write_js () {
local html_tempfile=$1
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
}

opt_chk () {
while getopts d:n:p:t:o: opt
do
   case $opt in
       d)
       SRC_TYPE="dir"
       logdir=$OPTARG
       if [ -d $logdir ];then
	   echo "OK,logdir is $logdir"
       else
	   echo "there is not directory named $logdir."
	   exit 1
       fi
	   ;;
       n)
       limit_num=`ls $logdir|tr " " "\n"|grep ".log"$|wc -l`
       filenum=$OPTARG
       if [ $filenum -gt $limit_num ];then
	   echo "Input filenum exceed filenum[$limit_num] in $logdir"
	   exit 1
       fi
           ;;
       p)
       _p=$OPTARG
       ppid_ck $_p
       if [ $log_count -eq 0 ];then
	   echo "no expect process.end"
	   exit 1
       fi
	   ;;
       t)
       GET_TYPE="_tail"
       linenum=$OPTARG
	   ;;
       o)
       GET_TYPE="_sed"
       s_word=`echo $OPTARG|awk -F':' '{print $1}'`
       e_word=`echo $OPTARG|awk -F':' '{print $2}'`
	   ;;
       ?)usage_error;exit 1;;
   esac
done
}
#main process##################################################
if [ $# -lt 1 ];then
   usage_error
   exit 1
fi


opt_chk $*


[ -d $html_dir ] || mkdir -p $html_dir
case $SRC_TYPE in
    "dir")
	case $GET_TYPE in
	    "_tail")
		write_html $html_tempfile DIR _TAIL
		;;
	    "_sed")
		write_html $html_tempfile DIR _SED
		;;
	esac
	;;
esac

write_js $html_tempfile

firefox $html_tempfile

#main process#################################################
