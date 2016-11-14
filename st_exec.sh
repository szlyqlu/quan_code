#!/bin/bash
# use multixterm
# build and change log
# changed at 2016/10/24
# change the serverlist to avoid the repeat server 2016/7/1
# add watch log fun 2016/9/28
# change watchlog script 2016/10/7
# change the after fun,use better algorithm. 2016/10/12
# continue to change the after fun,use pid to count the live process. \
# del the watch log script,because there is a new one.2016/10/24
# version 0.7

EXP_SH="./tempexp.exp"
EXP_SH_ADD="./tempexp_other.exp"
WATCH_SH="./watch.sh"
RUN_CMD="multixterm"

#LOG_DIR=`date +%Y%m%d`
#[ -d $LOG_DIR ]||mkdir -p $LOG_DIR

SET_LOGDIR () {
read -p "Do you want to customize your directory of logfile(yes|no)?" LOG_ANS
case $LOG_ANS in
YES|yes|y|Y)
	echo "*********************************************"
	ls -l|grep "^d"
        echo "*********************************************"
	read -p "choose or input a new directory: " LOG_DIR
        echo "*********************************************"
	if [ -d $LOG_DIR ];then
            OLD_LOG_COUNT=`ls -t $LOG_DIR|grep ".log$"|tr " " "\n"|wc -l`
        else
            OLD_LOG_COUNT=0
            mkdir -p $LOG_DIR
        fi
	;;
*)
        echo "*********************************************"
	DEF_LOG_DIR=`date +%Y%m%d`
	LOG_DIR=$DEF_LOG_DIR
	if [ -d $LOG_DIR ];then
            OLD_LOG_COUNT=`ls -t $LOG_DIR|grep ".log$"|tr " " "\n"|wc -l`
        else
            OLD_LOG_COUNT=0
            mkdir -p $LOG_DIR
        fi
	;;
esac
}

RUN_CHECK () {
rum_cd=$1
which $rum_cd>/dev/null 2>&1
if [ $? -ne 0 ];then
   echo "*********************************************"
   echo "the PC don't install $rum_cd,please install it first."
   echo "Includes expectk,tk etc."
   echo "*********************************************"
   exit 1
fi
}

EXEC_CMD () {
EXEC_EXP=$1
read -p "please input your serverlist: (use space to split)" -a SERVERLIST
if [ -z $SERVERLIST ];then
    echo "*********************************************"
    echo "you input error.end"
    echo "*********************************************"
    exit 1
fi
#AVOID repeat server
NEW_SERVERLIST=`echo ${SERVERLIST[*]}|sed "s/ /\n/g"|sort -u`
multixterm -xc "$EXEC_EXP %n" $NEW_SERVERLIST &
_PPID=`echo $!`
}

GET_USERID () {
echo "*********************************************"
read -p "please input your id:" USERID
echo "*********************************************"
}

CREATE_EXP () {
EXP_NAME=$1
LOG_DIR_NAME=$2
USERID=$3
[ -f $EXP_NAME ]&&rm $EXP_NAME

cat>$EXP_NAME<<EOF
#!/usr/bin/expect -f
#exp_sh is created at $(date)
set HOST [lindex \$argv 0]
set nowtime [exec date +%Y%m%d%H%M]
set timeout 10
log_file $LOG_DIR_NAME/\$HOST.\$nowtime.log
spawn ssh $USERID@\$HOST
interact
EOF

chmod 755 $EXP_NAME
}

CREATE_EXP_OTHER () {
EXP_NAME_ADD=$1
LOG_DIR_NAME_ADD=$2
[ -f $EXP_NAME_ADD ]&&rm $EXP_NAME_ADD

cat>$EXP_NAME_ADD<<EOF
#!/usr/bin/expect -f
#exp_sh is created at $(date)
set USERID [lindex \$argv 0]
set HOST [lindex \$argv 1]
set nowtime [exec date +%Y%m%d%H%M]
log_file $LOG_DIR_NAME_ADD/\$HOST.\$nowtime.log
spawn ssh \$USERID@\$HOST
interact
EOF

chmod 755 $EXP_NAME_ADD
}


CREATE_WATCH_SH () {
local LOGDIRNAME=$1
[ -f $WATCH_SH ]&&rm -f $WATCH_SH
cat>$WATCH_SH<<EOF
#!/bin/bash
#this is a test for watch log
#created at $(date)

log_key="expect -f"
log_count=\`ps -ef|grep -v grep|grep "\$log_key"|wc -l\`

if [ \$log_count -eq 0 ];then
	echo "No new mutilxterm process.end"
	exit 0
fi

echo "=================================================="
echo "LOGDIR is [$LOGDIRNAME]."
echo "NEWLOG is [\$log_count]."
read -p "Input the number of line you want to watch : " line_num
echo "=================================================="
if [ -s \$line_num ];then
	line_num=10
fi
echo -e "\\033[32m WATCH AT \`date\`\\033[0m"
for i in \`ls -t $LOGDIRNAME|grep ".log$"|tr " " "\n"|head -\$log_count\`
do
	echo "=================================================="
	update_time=\`ls -l $LOGDIRNAME/\$i|awk '{print \$6,\$7,\$8}'\`
	echo -e "\\033[31m \$i \\033[0m \$update_time"
	echo "=================================================="
	cat $LOGDIRNAME/\$i|tail -\$line_num
	echo " "
done

EOF
chmod 755 $WATCH_SH
}

EXEC_AFTER () {
LOGDIRNAME=$1
OLDLOGCOUNT=$2
echo "*********************************************"
echo "Counting the failed server,please wait a moment."
echo "The failed server will be listed at below,if blank.then every server is OK."
sleep 5
echo "*********************************************"
ALL_LOG_COUNT=`ls -t $LOGDIRNAME|grep ".log$"|tr " " "\n"|wc -l`
NEW_LOG_COUNT=`expr $ALL_LOG_COUNT - $OLDLOGCOUNT`
FAIL_COUNT=0
#old count of failed login
#for i in `ls -t $LOGDIRNAME|grep ".log$"|tr " " "\n"|head -$NEW_LOG_COUNT`
#do
#    cat $LOGDIRNAME/$i|egrep -q "Name or service not known|closed by remote host|WARNING: POSSIBLE DNS SPOOFING DETECTED|WARNING: REMOTE HOST IDENTIFICATION"
#    if [ $? -eq 0 ];then
#       cat $LOGDIRNAME/$i|head -1|cut -d'@' -f2
#       FAIL_COUNT=`expr $FAIL_COUNT + 1`
#    fi
#done
#comment at 2016/10/12
log_key="expect -f"
live_count=`ps -ef|grep -v grep|grep "$log_key"|grep $_PPID|wc -l`
FAIL_COUNT=`expr $NEW_LOG_COUNT - $live_count`
live_list=`ps -ef||grep -v grep|grep "$log_key"|grep $_PPID|awk '{print $NF}'`
for i in `echo ${NEW_SERVERLIST[*]}`
	do
 	    if ! echo $live_list|grep -qw $i;then echo $i;fi
	done
echo "*********************************************"
echo "Failed server count is [$FAIL_COUNT]."
echo "*********************************************"
echo "DONE.you can get log from [$LOGDIRNAME]"
echo "if you want to add new ssh by other userid,use $EXP_SH_ADD userid hostname"
echo "if you want to use same userid,just use $EXP_SH hostname"
echo "if you want to watch log at the sametime,use foldmkhtml.sh.PPID is [$_PPID]"
echo "*********************************************"
}


#====================Main Process==========================
RUN_CHECK $RUN_CMD

GET_USERID

SET_LOGDIR

CREATE_EXP $EXP_SH $LOG_DIR $USERID

EXEC_CMD $EXP_SH

CREATE_EXP_OTHER $EXP_SH_ADD $LOG_DIR

EXEC_AFTER $LOG_DIR $OLD_LOG_COUNT

#CREATE_WATCH_SH $LOG_DIR
#====================Main Process==========================
