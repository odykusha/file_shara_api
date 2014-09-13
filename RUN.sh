#!/bin/bash
#
# Python with Flask
#
# chkconfig: 2345 90 10
# description: Flask starter

#set -xue
Flask_PROC=`ps aux|grep python|grep file_shara|awk {'print $2'}|head -1`
DATE=`date`

case "$1" in
	        start)
			if [ -z "$Flask_PROC" ]; then
				cd /export/home0/file_shara
				./file_shara.py 2>>./logs/server.log >>./logs/server.log &
				date +'                  '[%d/%b/%Y' '%H:%M:%S]]" \"SERVER STOPED\"" >> ./logs/server.log
				echo "======= $DATE ======="
				echo "Flask started"
			else
				echo "======= $DATE ======="
				echo "Flask is already running. PID=$Flask_PROC Stop it first."
			fi
		;;
		stop)
			if [ ! -z "$Flask_PROC" ]; then
				echo "Killing: $Flask_PROC"
				kill -15 $Flask_PROC
				date +'                  '[%d/%b/%Y' '%H:%M:%S]]" \"SERVER STOPED\"" >> ./logs/server.log
			else
				echo "not found proces $Flask_PROC"
			fi
		;;
        	status)
			if [ -z "$Flask_PROC" ]; then
				echo "===================================================="
				echo "Flask is not running! Maybe something bad had happen?"
			else
				echo "==============================="
				echo "Flask is running, PID= $Flask_PROC"
			fi
		;;
		restart)
			./FS stop
			sleep 1
			./FS start
		;;
		
		gunicorn)
   			gunicorn file_shara:app -b 0.0.0.0:80 -w 5 --timeout 7200 --log-file /export/home0/file_shara/gunicorn.log &

		;;			
		*)
			echo "Usage: $0 {start|stop|restart|status}"
		;;
esac
exit
