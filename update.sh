#!/bin/bash

cd ~/farm3d
git fetch --all &&  git reset --hard && git pull
chmod 777 *
killall python3 mq.py