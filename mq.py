import time
import random
import requests
import json
from configparser import ConfigParser
import paho.mqtt.client as paho
import os
from PIL import Image
import io
from PIL import UnidentifiedImageError
from PIL import ImageFile
import subprocess
from requests import get, post,delete
from urllib.parse import urlparse
import fcntl
import sys
import _thread
import requests
from tqdm import tqdm
import socket
import subprocess
import json

import netifaces as ni
import asyncio
import datetime
from websockets.sync.client import connect
from datetime import datetime



from minio import Minio
import urllib3
from urllib.parse import urlparse
import certifi
from minio.commonconfig import REPLACE, CopySource
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)







home_path = os.path.dirname(os.path.realpath("~"))
#printer_name = "3-8"


#cfg
cfgfile = ConfigParser()
cfgfile.read("./klipper_config.cfg")
#var
broker = (cfgfile.get("Broker", "IP"))
topic = (cfgfile.get("MQTT-Config", "topic")) + '/'
#client_id = (cfgfile.get("MQTT-Config", "client_id"))
username = (cfgfile.get("Broker", "Username"))
password = (cfgfile.get("Broker", "Password"))
refresh_time = (cfgfile.get("MQTT-Config", "refresh_time"))
port = (cfgfile.get("Broker", "Port"))
isOpen = (cfgfile.get("MQTT-Config", "isOpen"))

ipmac = ni.ifaddresses('eth0')[ni.AF_LINK][0]["addr"]
ipmac = ipmac.translate({ord(':'): None})

secure = True
ok_http_client=urllib3.PoolManager(
            timeout=urllib3.util.Timeout(connect=10, read=10),
            maxsize=10,
            cert_reqs='CERT_NONE',
            ca_certs= os.environ.get('SSL_CERT_FILE') or certifi.where(),
            retries=urllib3.Retry(
                total=5,
                backoff_factor=0.2,
                status_forcelist=[500, 502, 503, 504]
            )
        )
minioClient = Minio(broker+":9000",
                   access_key='printer_download',
                    secret_key='12345678',
                    http_client=ok_http_client,
                    secure=secure)

print(minioClient.list_buckets())

#minioClient.fget_object("usebucket", "y_PLA_38m36s.gcode", "3DBenchy_PLA_38m36s.gcode")

#upload_file("/home/mks/printer_data/gcodes/Test6g-55m49s.gcode","a/")
#result = minioClient.fput_object(
#        "users-bucket", "/f@126.com/Test6g-55m49s.gcode","/home/mks/printer_data/gcodes/Test6g-55m49s.gcode"
 #   )



printer_name = (str(os.popen('cat /etc/hostname').read())+":"+ipmac).replace("\n", "")

#client_id = printer_name
image_timer = 60.0

wakeup = 1
time_old = time.time() 
downloading = 0


#print('wget http://127.0.0.1/server/job_queue/job?filenam'.replace("wget", ""))

all_notify =''

down_size = 0
total_size = 0
name_down_file =''
update_gcode_list = 0
notify_flag = 1
folders = {'config':'','gcodes':'','timelapse':'','logs':''}

files=requests.get(url="http://127.0.0.1/server/files/roots")
for folder in files.json()["result"]:
    if folder["name"] == 'config':
        folders['config'] = folder["path"]+'/'
    elif folder["name"] == 'gcodes':
        folders['gcodes'] = folder["path"] +'/'  
    elif folder["name"] == 'timelapse':
        folders['timelapse'] = folder["path"]+'/'   
    elif folder["name"] == 'logs':
        folders['logs'] = folder["path"] +'/'      
print(folders)

def websocket_thread(arg1,arg2):
    global all_notify
    global notify_flag
    with connect("ws://localhost:7125/websocket") as websocket:
        while True:
       # websocket.send("Hello world!")
            message = websocket.recv()
            message=json.loads(message)
           
            if 'notify_gcode_response'  in message["method"]:
                
                tmp_s = json.dumps(message["params"]).replace('[','')
                tmp_s = tmp_s.replace(']','')
                tmp_s = tmp_s.replace('"','')
                if 'B:' in tmp_s and 'T0:' in tmp_s:
                    continue
               # print( message) 
                

                current_time = datetime.now().time()
                notify_flag=1
                all_notify += str(current_time).split(".")[0]+"    "+tmp_s + '\n'
                
                

_thread.start_new_thread( websocket_thread,('ws',' '))




def upload_file(remotefile: str,local_path: str,file_name:str):
    if '/gcodes' in local_path:
        local_path = folders['gcodes']
    elif '/config' in local_path:
        local_path = folders['config']
    elif '/timelapse' in local_path:
        local_path = folders['timelapse']
    elif '/logs' in local_path:
        local_path = folders['logs']
        
    print(local_path+file_name)
    print(remotefile)
    result = minioClient.fput_object(
        "users-bucket",remotefile, local_path+file_name
        )
    print(
            "created {0} object; etag: {1}, version-id: {2}".format(
                result.object_name, result.etag, result.version_id,
            ),
        )

def download(url: str, fname: str):
    global total_size
    global down_size
    global name_down_file

    url = url.replace("users-bucket/", "")
    print("download url..."+url)
    url = url.split(":9000/"); 
   # minioClient.fget_object("users-bucket", url[1], fname)
    object_data = minioClient.get_object('users-bucket', url[1])
    total_size = int(object_data.headers.get('content-length', 0))
    print(str(total_size))
    with open(fname, 'wb') as file_data:
        for data in object_data:
            size = file_data.write(data)
            down_size +=size
    file_data.close()
     
   # print(asyncio.run(minioClient.get_object('users-bucket', url[1])))
    
    requests.post(url="http://127.0.0.1/server/job_queue/job?filenames="+name_down_file)
    return
    
    resp = minioClient.get_object('users-bucket', url[1]) #requests.get(url, stream=True)
    total_size = int(resp.headers.get('content-length', 0))
    print(str(total_size))
    # Can also replace 'file' with a io.BytesIO object
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
         
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            down_size +=size
            if down_size == total_size:
                print("downlaod finished:"+name_down_file)
                requests.post(url="http://127.0.0.1/server/job_queue/job?filenames="+name_down_file)
           # bar.update(size)




#download("http://47.121.215.229:9000/werf/3DBenchy_PLA_21m56s.gcode",'./test.gcode')

#while True:
#    time.sleep(1)
#    print("tot_size:"+str(int(down_size*100/total_size))+"%")
    

#printer_name = (cfgfile.get("MQTT-Config", "printer_name"))

print("printer_name:"+printer_name)


def get_thumbs_path(g_file):
    path_s = requests.get(url="http://127.0.0.1/server/files/metadata?filename="+g_file).json() 

   # print(path_s["result"]["thumbnails"][0]["size"])
  #  print(path_s["result"]["thumbnails"][1]["size"])
    if path_s["result"]["thumbnails"][0]["size"] > path_s["result"]["thumbnails"][1]["size"]:
        print(path_s["result"]["thumbnails"][0]["relative_path"])
        return path_s["result"]["thumbnails"][0]["relative_path"]
    else:
        print(path_s["result"]["thumbnails"][1]["relative_path"])
        return path_s["result"]["thumbnails"][1]["relative_path"]


if int(isOpen) == 0 :
    exit(0)

def C_publish(client,topics,json_s):
    #json = "{\"printer\":\"3-9\",\"temperature\":\""+str_data+"\"}"
    json_s["printer"] = printer_name
    show_title_IP = ''
    try:
        IP_addres = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
        if "192.168" in IP_addres:
        #logging.debug("IP_addres %s" % (IP_addres))
            show_title_IP = IP_addres
    except Exception as e:
        pass

    try:
        IP_addres = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
        if "192.168" in IP_addres:
        #logging.debug("IP_addres wlan0 %s" % (IP_addres))
            show_title_IP = IP_addres
    except Exception as e:
        pass
    json_s["IP"] = "http://"+show_title_IP
    #print(topics +printer_name)
    client.publish(topics+printer_name,json.dumps(json_s))

def Image_publish(client,topics,url,format,type):
    #print(url)
    r_data = requests.get(url, stream=True)
    #print(len(str(r_data.content)))
    if len(str(r_data.content)) <1024:
        return
    camera = Image.open(requests.get(url, stream=True).raw)
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    imgByteArr = io.BytesIO()
    camera.save(imgByteArr, format)
    imgByteArr = imgByteArr.getvalue()
    #print(io.BytesIO(camera))

    b = bytearray()
    b.extend(map(ord, printer_name+';'+type+';'))
    b.extend(imgByteArr)
    client.publish(topics+printer_name, b, 0)
    
    print("Image_ topics:"+topics+" url:"+ url)

def Image_publish_latest_print_file():
    global update_gcode_list
    update_gcode_list = 1
    #status_p = requests.get(url="http://127.0.0.1/printer/objects/query?webhooks&virtual_sdcard&print_stats&extruder=target,temperature&heater_bed=target,temperature")
    statues_file = str(status_p.json()["result"]["status"]["print_stats"]["filename"])
    #print(statues_file)
    if ".gco" in statues_file:
        try:
            Image_publish(client,topic + "printer_jpg","http://127.0.0.1/server/files/gcodes/"+get_thumbs_path(statues_file),'PNG','thu')
        except KeyError:
            return     
        return
    history = requests.get(url="http://127.0.0.1/server/database/item?namespace=history").json()
    latest_time = 0.0
    #print(history["result"]["value"])
    latest_id = ""
    try:
        for id in history["result"]["value"]:
            time_d= history["result"]["value"][id]["start_time"]
            if latest_time < time_d:
                latest_time = time_d
                latest_id = id
        history_file = history["result"]["value"][latest_id]["filename"]
        Image_publish(client,topic + "printer_jpg","http://127.0.0.1/server/files/gcodes/"+get_thumbs_path(history_file),'PNG','thu')        
    except KeyError:
        return 
   # print(history["result"]["value"][latest_id]["start_time"])
   # print(history["result"]["value"][latest_id]["filename"])
    
    #return history["result"]["value"][latest_id]["filename"]


def image_update(type):
    if 'camera' in type:
        Image_publish(client,topic + "printer_jpg","http://127.0.0.1/webcam/?action=snapshot",'JPEG','cam')
    else:
        Image_publish_latest_print_file()
        
def on_connect(client,userdata,flags,rc,mq):

    if rc == 0:
        print("connected with result code:" + str(rc))
        client.subscribe(topic + printer_name +"/control/run_gcode")
    else:
        # 如果链接断开，尝试重新连接
        print("Failed to reconnect to MQTT broker")
        
def on_disconnect(client,userdata,rc,mq1,mq2):
    if rc != 0:
        print("disconnented from MQTT :"+str(rc))
    	
def is_file_download(path,name):
    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)

        if os.path.isfile(file_path):
            print(file)
            if file == name:
                print("the file is aready there,no need to downlaod")
                return 1
            

        elif os.path.isdir(file_path):
            continue
    return 0


def on_message(client, userdata, message):
    global image_timer
    global wakeup
    global time_old
    global down_size
    global total_size
    global name_down_file
    
    print(f"{message.topic},{json.loads(str(message.payload.decode('utf-8')))['name']}")

    wakeup = 1
    time_old = time.time()
    if (message.topic) == (topic + printer_name +"/control/run_gcode"):
        name = json.loads(str(message.payload.decode('utf-8')))['name']
        mes_str = str(name)
        if 'jpg' in mes_str:
            
            image_update(str(name))
          #  image_timer = json.loads(str(message.payload.decode('utf-8')))['time']
           # print(image_timer)
           # image_time = float(str(name).find('jpg_time:'))
        elif 'wget' in mes_str:
           
           # result = subprocess.run(mes_str + ' -P /home/mks/printer_data/gcodes/', shell=True)
            
            #resultd = subprocess.Popen(mes_str + ' -P /home/mks/printer_data/gcodes/', shell=True, stdout=subprocess.PIPE)
            #print(os.path.basename(urlparse("wget  http://47.121.215.229:9000/werf/3DBenchy_PLA_21m56s.gcode").path))
            #if(value_json["print_stats"]["state"] == "printing")
            
            if down_size < total_size: # the last is still downloading
                return
            a = urlparse(mes_str) 
            down_size = 0
            total_size = 0
            name_down_file = os.path.basename(a.path)
            url = mes_str.replace("wget", "")
            path =  folders['gcodes'] + name_down_file
            print("url:"+url)
            print("path:"+path)
            
            if(is_file_download(folders['gcodes'],name_down_file) == 1):
                requests.post(url="http://127.0.0.1/server/job_queue/job?filenames="+name_down_file)
                return
            
            _thread.start_new_thread( download, (url, path) )
            #download(url,path)
           # fcntl.fcntl(resultd.stdout, fcntl.F_SETFL, os.O_NONBLOCK)
            #sys.stdout.flush()
            
            
            
            # print (result)
            #print("enqueue file:"+os.path.basename(a.path))
            #requests.post(url="http://127.0.0.1/server/job_queue/job?filenames="+os.path.basename(a.path))
            
            
           # requests.post(url="http://127.0.0.1/printer/print/start?filename="+os.path.basename(a.path))
        elif '/server/job_queue/start' in mes_str:
            print("job queue start")
            requests.post(url="http://127.0.0.1/server/job_queue/start")            
        elif 'DELETE /server/job_queue/job?job_ids' in mes_str:
            new_str = mes_str.split( ); 
            print("http://127.0.0.1/"+new_str[1])
            requests.delete(url="http://127.0.0.1"+new_str[1])            
        elif '/server/job_queue/jump?job_id=' in mes_str:
            print("http://127.0.0.1/"+mes_str)
            requests.post(url="http://127.0.0.1"+mes_str)             
        elif '/server/job_queue/status' in mes_str:
            print("send job queue files")
            q_status_p = requests.get(url="http://127.0.0.1/server/job_queue/status")
            
            #status_p = requests.get(url="http://127.0.0.1/printer/objects/query?webhooks&virtual_sdcard&print_stats&extruder=target,temperature&heater_bed=target,temperature")
        elif 'update_eryone_app' in mes_str:
            try:
                subprocess.run(["../mainsail/all/git_pull.sh", ""])
            except KeyError:
                pass    
        elif 'update_farm3d_app' in mes_str:        
            try:
                subprocess.run(["./update.sh", ""])
            except KeyError:
                pass            
                
        elif 'POST /' in mes_str:
            command = "http://127.0.0.1" + str(name).replace("POST ", "").replace("\n","")
            requests.post(url=command)
        elif 'DELETE /' in mes_str:
            command = "http://127.0.0.1" + str(name).replace("DELETE ", "").replace("\n","")
            print(command)
            requests.delete(url=command)    
        elif 'upload_file_to_cloud:' in mes_str:
            local_folder_name =  str(name).split(":")[2] #"/home/mks/printer_data/logs/klippy.log"
            file_name =  str(name).split(":")[3].replace("\n","")
            remote_user = str(name).split(":")[1]
            #local_file =  str(name).replace("upload_file_to_cloud:", "").replace("\n","") #"/home/mks/printer_data/logs/klippy.log"
            upload_file("/"+remote_user+"/"+printer_name.split(':')[0]+"_"+file_name,local_folder_name,file_name)
            
        else:
            requests.get(url="http://127.0.0.1/printer/gcode/script?script=" + str(name))


client= paho.Client(paho.CallbackAPIVersion.VERSION2,printer_name,transport="websockets")
client.on_message=on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.reconnect_delay_set(min_delay=1,max_delay=120)

client.username_pw_set(username, password)
#client.tls_set()
#client.tls_set(ca_certs="./emqxsl-ca.crt")
#client.tls_set(ca_certs="./demo.crt")

#client.ws_set_options(path="/mqtt")






if int(port) > 0 :
    print(broker)
    print(port)
    client.connect(broker, int(port))
else :
    client.connect(broker)


client.loop_start()

#Image_publish(client,topic + "/camera_jpg","http://127.0.0.1/server/files/gcodes/.thumbs/"+history_file.split('.')[0]+"-400x400.png",'PNG')

status_p = requests.get(url="http://127.0.0.1/printer/objects/query?webhooks&virtual_sdcard&print_stats&extruder=target,temperature&heater_bed=target,temperature")


#requests.post("http://127.0.0.1", "printer/print/start", "filament_.gcode").json()


while True:
    #time.sleep(3)
    if wakeup == 1:
        time.sleep(2)
    else:
        time.sleep(3)
        
    status_p = requests.get(url="http://127.0.0.1/printer/objects/query?webhooks&virtual_sdcard&print_stats&extruder=target,temperature&heater_bed=target,temperature")
    q_status_p = requests.get(url="http://127.0.0.1/server/job_queue/status")
    try:
        value_json = status_p.json()["result"]
        value_json["queued_jobs"] = q_status_p.json()["result"]["queued_jobs"]
        value_json["console_log"] =  ''
        if notify_flag == 1:
            notify_flag =0
            value_json["console_log"] =  all_notify
            
        ###download process
        if down_size == total_size:
            value_json["queue_state"] = "" #q_status_p.json()["result"]["queue_state"]
        else :
            progress = int(down_size*100/total_size)
            value_json["queue_state"] = "  Downloading "+name_down_file+"("+str(progress)+"%)"
            print("tot_size:"+value_json["queue_state"])

        ####
        if update_gcode_list == 1:
            q_list_file = requests.get(url="http://127.0.0.1/server/files/list?root=gcodes")
            value_json["gcodes_list"] = q_list_file.json()["result"]
            q_list_file = requests.get(url="http://127.0.0.1/server/history/list")
            value_json["history_list"] = q_list_file.json()["result"]["jobs"]
            q_list_file = requests.get(url="http://127.0.0.1/server/files/list?root=timelapse")
            value_json["timelapse_list"] = q_list_file.json()["result"]
            value_json["console_log"] =  all_notify
            update_gcode_list = 0
            
        #print(value_json)
        C_publish(client,topic + "printer_status/temperature/tool0/actual", value_json)
    except KeyError:
        pass 

    if (time.time() - time_old)>30 and (wakeup==1) :
        wakeup = 0
        print("go to sleep..")

            
    #    image_update('')
       # image_update('camera')
       # time_old = time.time()
    

