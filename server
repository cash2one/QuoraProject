#!/bin/bash
#$ -cwd
#$ -V
#$ -N ScrapeServer
#$ -S /bin/bash
#$ -M willipovell@gmail.com
#$ -m eas
#$ -j y -o /export/a04/wpovell/logs
#$ -l mem_free=1G,ram_free=1G

echo "**********************************************************************"
echo "Finding an available port..."
declare -A un_ports
for used in $(netstat -antu | perl -pe 's/ +/ /g;' | tail -n+3 | cut -f4 -d' ' | cut -f2 -d':' | grep -P '\d{4,}'); do
    un_ports[$used]=1
done
bad_port=1
MST_PORT=
while [ $bad_port == 1 ]; do
    option=$(shuf -i 1025-44999 -n1)
    echo -en "trying port $option... "
    if [ ${un_ports[$option]:-abc} == "abc" ]; then
	MST_PORT=$option
	bad_port=0
	echo "which is good"	
    fi
done
echo "Available port found: $(hostname):$MST_PORT"

python -u -m Quora.ScrapeServer $MST_PORT -o /export/a04/wpovell/scrape_data
