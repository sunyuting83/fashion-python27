 #!/bin/bash
while true  
do
  pid=$(lsof -i:5002|awk '{print $2}')
  #echo ${pid}
  if [ ! -n "${pid}" ];then
    echo "restart..."
    basepath=$(cd `dirname $0`; pwd)
    export PATH=/sbin:/bin:/usr/bin
    cd $basepath
    python run.py
  fi
  sleep 5
done