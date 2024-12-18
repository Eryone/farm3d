#!/usr/bin/env bash

killall python3 mq.py
uptime | tee -a /home/mks/printer_data/logs/mq.log
sleep 3 
cd /home/mks/KlipperScreen/mqtt/ 
chmod 777 *
python3 /home/mks/KlipperScreen/mqtt/mq.py 

