# farm3d


### Installation


#### 1. Download the software
```
cd ~
git clone https://github.com/Eryone/farm3d.git
```
#### 2. install the software as a service

modify the  the `User=` `WorkingDirectory=` `ExecStart=` to your actuall path in the file farm3d.service.
```
nano ~/farm3d/farm3d.service
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
