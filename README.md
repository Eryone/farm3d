# Farm3D

![page0](https://github.com/Eryone/farm3d/blob/main/doc/mainpage.png)


### Installation


#### 1. Download the software
```
cd ~
git clone https://github.com/Eryone/farm3d.git
```
#### 2. Install the required software
```
cd ~/farm3d/
chmod 777 ~/farm3d/*
./install.sh
```

#### 3. Enable it auto start after printer boot.
```
sudo cp ~/farm3d/farm3d.service    /etc/systemd/system/
sudo systemctl  daemon-reload
sudo systemctl  enable farm3d.service
sudo systemctl  restart farm3d.service

```

#### 4. goto https://eryone.club then add your printer in the webpage

How to add new Printer:  https://youtube.com/shorts/0iYtUhFUCZc
Review: https://youtu.be/-Sf5vfT637g

That's all, happy printing!



