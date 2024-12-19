#!/bin/bash

## replace to local home dir
path=$(echo ${HOME} | sed 's/\//\\\//g')
sed -i 's/~/'"$path"'/g'  ./farm3d.service
#echo $path


pip3 install websockets
#pip3 install opencv-python
#pip3 install qrcode[pil]
pip3 install paho-mqtt
pip3 install requests
pip3 install ConfigParser
pip3 install typing-extensions
pip3 install Pillow
pip3 install tqdm
pip3 install netifaces
pip3 install minio

exit

