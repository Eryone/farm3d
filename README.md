# Farm3D

![page0](https://github.com/Eryone/farm3d/blob/main/doc/mainpage.png)


### Installation


#### 1. Download the software
```
cd ~
git clone https://github.com/Eryone/farm3d.git
chmod 777 ~/farm3d/*
```
#### 2. Install the software as a service


```
cd ~/farm3d/
./install.sh
```


enable the service and reboot your printer.
```
sudo cp ~/farm3d/farm3d.service    /etc/systemd/system/
sudo systemctl  daemon-reload
sudo systemctl  enable farm3d.service
sudo systemctl  restart farm3d.service

```

#### 3. goto https://eryone.club then add your printer in the webpage

That's all, happy printing!



