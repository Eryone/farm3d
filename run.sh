#!/usr/bin/env bash
killall python3 mq.py
#uptime | tee -a /home/mks/printer_data/logs/mq.log
sleep 3 
cd ~/farm3d/ 
chmod 777 *
python3 mq.py
